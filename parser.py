import re
import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver


# Сайты для парсинга:
BOOSTER_PRICES = 'https://www.steamcardexchange.net/index.php?boosterprices'
BADGE_PRICES = 'https://www.steamcardexchange.net/index.php?badgeprices'
PREFIX_LINK = 'https://www.steamcardexchange.net/'
STEEM_PREFIX_LINK = 'https://steamcommunity.com/market/search?appid=753&category_753_Game%5B%5D=tag_app_'

PATTERN_PRICE = r'\$.*'
MULTIPLIER = 3*0.55
TABLE_TRANSLATE = {
    '0.03': 0.01,
    '0.04': 0.02,
    '0.05': 0.03,
    '0.06': 0.04,
    '0.07': 0.05,
    '0.08': 0.06,
    '0.09': 0.07,
    '0.1': 0.08,
    '0.11': 0.09,
    '0.12': 0.1,
    '0.13': 0.11,
    '0.14': 0.12,
    '0.15': 0.13,
    '0.16': 0.14,
    '0.17': 0.15,
    '0.18': 0.16,
    '0.19': 0.17,
    '0.2': 0.18,
    '0.21': 0.19,
    '0.22': 0.19,
    '0.23': 0.2,
    '0.24': 0.21,
    '0.25': 0.22,
}

def get_html(url):
    response = requests.get(url)
    return response.text

def parse_booster():
    # Настройка и инициализация браузера
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    browser = webdriver.Chrome(chrome_options=options, executable_path='/Users/ilaantonov/PycharmProjects/parser/chromedriver')
    # Для отображения браузера
    # browser = webdriver.Chrome(executable_path='/Users/ilaantonov/PycharmProjects/parser/chromedriver')
    # Вход на сайт и загрузка нужнойстраницы с полным перечнем игр
    browser.get(BOOSTER_PRICES)
    selector = browser.find_element_by_name('boosterpricelist_length')
    option = selector.find_elements_by_tag_name("option")[-1]# Установить -1 после отладки
    option.click()
    option.click()
    time.sleep(1)
    # Генерация html кода и выход из браузера
    generated_html = browser.page_source
    browser.quit()
    print('start')
    # Поиск ссылок на игры и формирование спска игр для возврата из функции
    soup = BeautifulSoup(generated_html, "html.parser")
    table = soup.find('table', id="boosterpricelist")
    result_link_list = []
    with open('all_links.txt', 'w') as fw:
        for teg_a in table.tbody.find_all('a'):
            link = PREFIX_LINK+teg_a['href']
            result_link_list.append(link)
            fw.write(link+'\n')
        print('stop')
    return result_link_list


# Поиск карт
def search_card(cards):
    prices_cards = []
    for card in cards:
        # print(card.a.text)
        try:
            price_dirty = re.search(PATTERN_PRICE, card.a.text).group()
            prices_cards.append(float(price_dirty[1:]))  # Записываем цены в список
        except AttributeError:
            # print('wrong card')
            pass
    return prices_cards

# Условие Покупки пака
def may_buy(booster_price, card_price):
    try:
        card_price = TABLE_TRANSLATE[str(card_price)]
    except KeyError:
        return False
    if booster_price < card_price*3:
        return True
    else:
        return False


# Поиск выгодных покупок
def search_profit_boosters(all_boosters):
    # Перебираем все ссылки на игры
    link_number = 0
    for booster_link in all_boosters:
        prices_cards = []
        try:
            response = requests.get(booster_link)
        except requests.exceptions.ConnectionError:
            print(response, response.url())
            print('Link number = ', link_number)
            time.sleep(60)
            response = requests.get(booster_link)

        link_number += 1

        soup = BeautifulSoup(response.text, 'html.parser')

        game_name = soup.find('div', class_='game-title').h1.text

        # Рассматриваем карточки
        id_cards = soup.find('div', id='cards')
        cards = id_cards.find_all('div', class_='element-button')
        prices_cards.extend(search_card(cards))

        # Рассматриваем foil карточки
        id_cards = soup.find('div', id='foilcards')
        cards = id_cards.find_all('div', class_='element-button')
        prices_cards.extend(search_card(cards))

        # Search booster pack price
        if soup.find('div', id='booster') == None:
            continue
        bp = soup.find('div', id='booster').find('div', class_='element-button').a.text
        price_bp = float(re.search(PATTERN_PRICE, bp).group()[1:])

        if price_bp < 0.5:
            if may_buy(price_bp, min(prices_cards)):
                print('YES   ' + game_name)
                print(price_bp, min(prices_cards))
                file.write(booster_link+'\t\n')
            else:
                print('NO    ' + game_name)

        # print(price_bp)
        # print(min(prices_cards))
        # print(min(prices_cards)*3*0.85*1.1)

def relink():
    with open('all_links.txt') as fr:
        with open('all_links_steam.txt', 'w') as fw:
            for line in fr.readlines():
                link = STEEM_PREFIX_LINK + line[59:]
                # print(link)
                fw.write(link)

parse_booster()
relink()
# print(parse_booster())
# with open('result.txt', 'w') as file:
    # parse_booster()
    # search_profit_boosters(parse_booster())
    # may_buy(0.08, 0.05)

