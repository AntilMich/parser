import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
import re
from selenium.webdriver.common.keys import Keys

# Сайты для парсинга:
BOOSTER_PRICES = 'https://www.steamcardexchange.net/index.php?boosterprices'
BADGE_PRICES = 'https://www.steamcardexchange.net/index.php?badgeprices'
PREFIX_LINK = 'https://www.steamcardexchange.net/'
PATTERN_PRICE = r'\$.*'
MULTIPLIER = 3*0.55

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
    # Поиск ссылок на игры и формирование спска игр для возврата из функции
    soup = BeautifulSoup(generated_html, "html.parser")
    table = soup.find('table', id="boosterpricelist")
    result_link_list = []
    for teg_a in table.tbody.find_all('a'):
        # if PREFIX_LINK+teg_a['href'] == 'https://www.steamcardexchange.net/index.php?gamepage-appid-575140':
            # print(len(result_link_list))
            # return result_link_list
        result_link_list.append(PREFIX_LINK+teg_a['href'])
    return result_link_list

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
            print('Link number = ' ,link_number)
            time.sleep(60)
            response = requests.get(booster_link)

        link_number += 1

        soup = BeautifulSoup(response.text, 'html.parser')

        game_name = soup.find('div', class_='game-title').h1.text

        # Рассматриваем карточки
        id_cards = soup.find('div', id='cards')
        cards = id_cards.find_all('div', class_='element-button')
        for card in cards:
            # print(card.a.text)
            price_dirty = re.search(PATTERN_PRICE,card.a.text).group()
            prices_cards.append(float(price_dirty[1:])) # Записываем цены в список

        # Рассматриваем foil карточки
        id_cards = soup.find('div', id='foilcards')
        cards = id_cards.find_all('div', class_='element-button')
        for card in cards:
            # print(card.a.text)
            try:
                price_dirty = re.search(PATTERN_PRICE, card.a.text).group()
                prices_cards.append(float(price_dirty[1:]))  # Записываем цены в список
            except AttributeError:
                # print('wrong card')
                pass

        # Search booster pack price
        if soup.find('div', id='booster') == None:
            continue
        bp = soup.find('div', id='booster').find('div', class_='element-button').a.text
        price_bp = float(re.search(PATTERN_PRICE, bp).group()[1:])

        if price_bp < 1:
            if price_bp < min(prices_cards)*MULTIPLIER:
                result_str = 'YES   ' + game_name
                print(result_str)
                print(price_bp, min(prices_cards), min(prices_cards)*3*0.55)
                file.write(booster_link+'\n')
            else:
                result_str = 'NO    ' + game_name
                print(result_str)
                # file.write(result_str+'\n')

        # print(price_bp)
        # print(min(prices_cards))
        # print(min(prices_cards)*3*0.85*1.1)

# print(parse_booster())
with open('result.txt', 'w') as file:
    # parse_booster()
    search_profit_boosters(parse_booster()[1150:])



