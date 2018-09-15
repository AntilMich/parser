import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import re


# def by_price_key(element):
#     return element.find('span', class_='normal_price').span.text

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
        print(div_price, div_price.text)
        count_and_price = re.findall(r'\d[\d,\.]*', div_price.text)
        print(count_and_price)
        price = float(count_and_price[1].replace(',', '.'))
        # span = soup.find('div', id='market_commodity_forsale').find_all('span')[1].text
        # real_price = float(span[:-5].replace(',', '.'))
        print(price)
        if price < max_cost_of_set:
            print('Я не хочу последнии копейки тратить с аккаунта(')

            # Покупает 1 товар по ссылке
            browser.find_element_by_class_name('btn_green_white_innerfade').click()
            time.sleep(0.5)
            browser.find_element_by_id('market_buyorder_dialog_accept_ssa').click()
            time.sleep(0.5)
            browser.find_element_by_id('market_buyorder_dialog_purchase').click()

    # time.sleep(200)

def login():
    browser = webdriver.Chrome(executable_path='/Users/ilaantonov/PycharmProjects/parser/chromedriver')
    browser.get('https://store.steampowered.com')
    browser.find_element_by_class_name('global_action_link').click()
    # Логин и пароль аккаунта steam
    browser.find_element_by_id('input_username').send_keys('ilia1219464')
    browser.find_element_by_id('input_password').send_keys('IlIa3417884')
    browser.find_element_by_class_name('btnv6_blue_hoverfade').click()

    # Время для логина в Steam ручками нужно делать, пока нет аккаунта без мобильной аутентификации
    time.sleep(15)
    return browser

def parse():
    result_card_sets = []
    with open('steamLinks.txt') as fr:
        with open('shouldToBye.txt', 'w') as fw:
            browser = login()

            # Перебираем ссылки на все игры
            for link in fr.readlines():
                markets_list = [] # Массив продоваемых элементов с игры
                time.sleep(1.51) # Задержка перед новым запросом для обхода бана (уточнить время!!!)
                print('--------------------NEW_LINK--------------------')
                browser.get(link)

                # Перебор страниц с элементани игры от одной игры
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                markets_list = (soup.find_all('a', class_="market_listing_row_link"))

                page_next = browser.find_element_by_id('searchResults_btn_next')
                pages_count = int(soup.find('span', id='searchResults_links').text[-2:-1])

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
                    fw.write(link+'\t\n')
                    print(card_min_price, card_set_price)
                    result_card_sets.append(link)
                    bye(card_set_link, card_min_price*0.9*0.85*3, browser)
            browser.quit()
    return result_card_sets


print(parse())
# bye('https://steamcommunity.com/market/listings/218620/MATEVER%20.357%20%7C%20Dragoon%2C%20Lightly-Marked', 0.12, webdriver.Chrome(executable_path='/Users/ilaantonov/PycharmProjects/parser/chromedriver'))
# print(float(re.search(r'\d[\d,]*', 'class="market_commodity_orders_header_promote">4,22 руб.</span>').group().replace(',', '.')))
# print(re.findall(r'\d[\d,]*', 'Лотов на продажу: 61Начальная цена: 4,22 pуб.'))
# bye('https://steamcommunity.com/market/listings/753/593330-Algotica%20Iterations%20Booster%20Pack', 1)