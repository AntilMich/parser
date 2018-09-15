# перебор эементоа игры! не правильный алгоритм поиска карточек и бустера

import re
import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver

BOOSTER_PRICES = 'https://www.steamcardexchange.net/index.php?boosterprices'
STEEM_PREFIX_LINK = 'https://steamcommunity.com/market/search?appid=753&category_753_Game%5B%5D=tag_app_'

# Настройка программы:

LOGIN = 'ilia1219464' # Логин Steam
PASSWORD = 'IlIa3417884' # Пароль Steam
# LOGIN = 'diggle98' # Логин Steam
# PASSWORD = 'FABZ6NNA83RW' # Пароль Steam
SHOULD_TO_BYE = False # Установить True для автоматической скупки паков
FIRST_GAME_INDEX = 3000
LUST_GAME_INDEX = 4000
TIME_TO_SLEEP = 1.55 # Настройка паузы между запросами
MAX_PACK_PRICE = 100 # Максимальная цена пака RUB
PATH_TO_WEBDRIVER = '/Users/ilaantonov/PycharmProjects/parser/chromedriver' # Путь до Webdriver
SEARCH_FORMULA = 0.9*3 # Формула для поиска выгодных карт. (Изменять первый коэффициент)
# SEARCH_FORMULA = 1.2*3 # Формула для поиска выгодных карт. (Изменять первый коэффициент)

WHAIT_FOR_ENTER_CODE = 30 # Установка времени на ожидание ввода кода подтверждения логина


def parse_booster(browser):

    print('start parse game links')
    browser.get(BOOSTER_PRICES)
    selector = browser.find_element_by_name('boosterpricelist_length')
    option = selector.find_elements_by_tag_name("option")[-1]  # Установить -1 после отладки
    option.click()
    option.click()
    time.sleep(TIME_TO_SLEEP)
    # Генерация html кода и выход из браузера
    generated_html = browser.page_source
    # Поиск ссылок на игры и формирование спска игр для возврата из функции
    soup = BeautifulSoup(generated_html, "html.parser")
    table = soup.find('table', id="boosterpricelist")
    result_link_list = []
    for teg_a in table.tbody.find_all('a'):
        link = STEEM_PREFIX_LINK + teg_a['href'][25:]
        result_link_list.append(link)
    return result_link_list


def should_to_bye(card_price, card_pak_price, count_set_on_market):
    if card_price == 0:
        return False
    elif (count_set_on_market > 10) & (card_price * SEARCH_FORMULA > card_pak_price) & (card_pak_price < MAX_PACK_PRICE):
        return True
    return False


def bye(link_to_bye, max_cost_of_set, browser):
    for i in range(3):
        time.sleep(TIME_TO_SLEEP)
        browser.get(link_to_bye)
        time.sleep(TIME_TO_SLEEP)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        div_price = soup.find('div', id='market_commodity_forsale')
        count_and_price = re.findall(r'\d[\d,\.]*', div_price.text)
        try:
            price = float(count_and_price[1].replace(',', '.'))
        except:
            continue

        if price < max_cost_of_set:
            print('Покупка предмета', price, '-', soup.find('h1', id='largeiteminfo_item_name').text)

            if SHOULD_TO_BYE:
                # Покупает 1 товар по ссылке
                browser.find_element_by_class_name('btn_green_white_innerfade').click()
                time.sleep(TIME_TO_SLEEP)
                browser.find_element_by_id('market_buyorder_dialog_accept_ssa').click()
                time.sleep(TIME_TO_SLEEP)
                browser.find_element_by_id('market_buyorder_dialog_purchase').click()


def login(browser):

    browser.get('https://store.steampowered.com')
    browser.find_element_by_class_name('global_action_link').click()

    # Логин и пароль аккаунта steam
    browser.find_element_by_id('input_username').send_keys(LOGIN)
    browser.find_element_by_id('input_password').send_keys(PASSWORD)
    browser.find_element_by_class_name('btnv6_blue_hoverfade').click()

    # Старый способ логина
    time.sleep(WHAIT_FOR_ENTER_CODE)

    # Новый способ логина
    # login_code = input('Введите код аутентификации: ')
    # browser.find_element_by_id('twofactorcode_entry').send_keys(login_code)
    # browser.find_element_by_id('login_twofactorauth_buttonset_entercode').find_element_by_class_name(
    #     'auth_button').click()
    #
    # time.sleep(2)
    print('Login sucsess...')

def search_pack_and_cards(link, browser):

    # login(browser) # Убрать после отладки

    browser.get(link)
    # time.sleep(TIME_TO_SLEEP)
    browser.find_element_by_class_name('market_listing_table_header').find_element_by_class_name('market_listing_right_cell').click()

    soup = BeautifulSoup(browser.page_source, 'html.parser')
    links_on_page = []

    page_next = browser.find_element_by_id('searchResults_btn_next')

    try:
        pages_count = int(soup.find('span', id='searchResults_links').text[-2:-1])
    except ValueError:
        print('error')

    for i in range(pages_count):
        time.sleep(TIME_TO_SLEEP)
        try:
            page_next.click()
        except:
            return 0, 0, 0, ''
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        links_on_page.extend(soup.find_all('a', 'market_listing_row_link'))

    try:
        game_name = re.search(r'из .*', links_on_page[0].find('span', class_='market_listing_game_name').text).group()[3:]
    except:
        return 0, 0, 0, ''
    print('-------------------- ' + game_name + ' --------------------')

    cards_prices = []

    for element in links_on_page:
        element_name = element.find('span', class_='market_listing_game_name').text
        try:
            # element_price = float(markets_element.find('span', class_='normal_price').span.text[1:-4])  #USD
            element_price = float(element.find('span', class_='normal_price').span.text[:-5].replace(',', '.'))  # RU
        except ValueError:
            element_price = 999
        if element_name == 'Коллекционная карточка из ' + game_name:
            cards_prices.append(element_price)
        if element_name == 'Набор карточек':
            pack_price = float(element_price)
            card_set_link = element['href']
            count_set_on_market = int(element.find('span', class_="market_listing_num_listings_qty").text)


    len_links_on_page = len(links_on_page)
    game_items_count = int(soup.find('span', id='searchResults_total').text)
    # print(game_items_count, ' == ', len_links_on_page)

    if len_links_on_page != game_items_count:
        for a in links_on_page:
            print(a.find('span', class_='market_listing_item_name').text, '\t', a.find('span', class_='market_listing_game_name').text)
        raise Exception('Parsing wrong: game_items_count != len_links_on_page')
        return 0, 0, 0, ''
    min_card_price = min(cards_prices)
    try:
        return (min_card_price, pack_price, count_set_on_market, card_set_link)
    except:
        return 0, 0, 0, ''

def parse():
    result_card_sets = []
    browser = webdriver.Chrome(executable_path=PATH_TO_WEBDRIVER)
    # time.sleep(500)
    link_list = parse_booster(browser)
    login(browser)

    with open('result.txt', 'a') as fw:

        len_list = len(link_list)

        # Перебираем ссылки на все игры
        for index, link in enumerate(link_list[FIRST_GAME_INDEX:LUST_GAME_INDEX]):
            try:
                print(index+FIRST_GAME_INDEX, ' of ', len_list)
                card_p, pack_p, count_set_on_market, set_link = search_pack_and_cards(link, browser)
            except:
                try:
                    print(index, ' of ', len_list)
                    card_p, pack_p, count_set_on_market, set_link = search_pack_and_cards(link, browser)
                except:
                    continue
            # print(card_p)
            # print(pack_p)

            if should_to_bye(card_p, pack_p, count_set_on_market):
                print(card_p, pack_p)
                result_card_sets.append(link)
                print('add Game lint to list and \'result.txt\' file')
                # bye(set_link, card_p * SEARCH_FORMULA, browser)
                fw.write(link + '\t\n')

    print('на этом всё, я не хочу быть забаненым\nПройдены игры с', FIRST_GAME_INDEX, ' по ', LUST_GAME_INDEX)
    browser.quit()
    return result_card_sets



print(parse())

