import re
import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver

BOOSTER_PRICES = 'https://www.steamcardexchange.net/index.php?boosterprices'
STEEM_PREFIX_LINK = 'https://steamcommunity.com/market/search?appid=753&category_753_Game%5B%5D=tag_app_'



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
        link = STEEM_PREFIX_LINK+teg_a['href'][25:]
        result_link_list.append(link)
    return result_link_list

def should_to_bye(card_price, card_pak_price, count_cards_in_set):
    if (count_cards_in_set > 10) & (card_price*0.9*3*0.85 > card_pak_price):
        return True
    return False

def bye(link_to_bye, max_cost_of_set, browser = webdriver.Chrome(executable_path='/Users/ilaantonov/PycharmProjects/parser/chromedriver')): # Тут крашится
    for i in range(3):
        time.sleep(1.51)
        browser.get(link_to_bye)
        time.sleep(1)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        div_price = soup.find('div', id='market_commodity_forsale')
        count_and_price = re.findall(r'\d[\d,\.]*', div_price.text)
        price = float(count_and_price[1].replace(',', '.'))

        if price < max_cost_of_set:
            print('Покупка предмета', price ,'-', soup.find('h1', id='largeiteminfo_item_name').text)


            # !!!!!!!!
            #Раскоментировать код для совершения покупок

            # Покупает 1 товар по ссылке
            browser.find_element_by_class_name('btn_green_white_innerfade').click()
            time.sleep(0.5)
            # browser.find_element_by_id('market_buyorder_dialog_accept_ssa').click()
            # time.sleep(0.5)
            # browser.find_element_by_id('market_buyorder_dialog_purchase').click()


            #!!!!!!!!

def login():
    browser = webdriver.Chrome(executable_path='/Users/ilaantonov/PycharmProjects/parser/chromedriver')
    browser.get('https://store.steampowered.com')
    browser.find_element_by_class_name('global_action_link').click()
    # Логин и пароль аккаунта steam
    browser.find_element_by_id('input_username').send_keys('ilia1219464')
    browser.find_element_by_id('input_password').send_keys('IlIa3417884')
    browser.find_element_by_class_name('btnv6_blue_hoverfade').click()

    # Время для логина в Steam ручками нужно делать, пока нет аккаунта без мобильной аутентификации
    time.sleep(3000)
    return browser

def parse(link_list):
    result_card_sets = []
    browser = login()
    with open('result.txt', 'w') as fw:

        # Перебираем ссылки на все игры
        for link in link_list:
            markets_list = [] # Массив продоваемых элементов с игры
            time.sleep(1.51) # Задержка перед новым запросом для обхода бана (уточнить время!!!)
            print('--------------------NEW_LINK--------------------')
            browser.get(link)

            # Перебор страниц с элементани игры от одной игры
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            markets_list = (soup.find_all('a', class_="market_listing_row_link"))

            page_next = browser.find_element_by_id('searchResults_btn_next')
            try:
                pages_count = int(soup.find('span', id='searchResults_links').text[-2:-1])
            except ValueError:
                continue

            for i in range(pages_count-1):
                # print(i, page_next)
                page_next.click()
                time.sleep(1.51)
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                markets_list += (soup.find_all('a', class_="market_listing_row_link"))

            card_min_price = 100
            card_set_link = ''
            card_set_price = 1000
            # markets_list.sort(key=by_price_key)
            count_cards_in_set = 0

            for markets_element in markets_list:
                element_type = markets_element.find('span', class_='market_listing_game_name').text

                try:
                    # element_price = float(markets_element.find('span', class_='normal_price').span.text[1:-4])  #USD
                    element_price = float(markets_element.find('span', class_='normal_price').span.text[:-5].replace(',', '.'))  # RU

                except ValueError:
                    element_price = 999

                if element_type == 'Набор карточек':
                    card_set_price = float(element_price)
                    card_set_link = markets_element['href']
                    count_cards_in_set = int(markets_element.find('span', class_="market_listing_num_listings_qty").text)

                if 'Коллекционная карточка' in element_type:
                    # print(element_price)
                    if card_min_price > element_price:
                        card_min_price = element_price

            if should_to_bye(card_min_price, card_set_price, count_cards_in_set):
                print(card_min_price, card_set_price)
                result_card_sets.append(link)
                bye(card_set_link, card_min_price*0.9*0.85*3, browser)
                fw.write(link+'\t\n')
    browser.quit()
    return result_card_sets


print(parse(parse_booster()))