import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time


# def by_price_key(element):
#     return element.find('span', class_='normal_price').span.text

def should_to_bye(card_price, card_pak_price):
    if card_price*0.9*3*0.85 > card_pak_price:
        return True
    return False

def parse():
    result_card_sets = []
    with open('steamLinks.txt') as fr:
        with open('shouldToBye.txt', 'w') as fw:
            browser = webdriver.Chrome(executable_path='/Users/ilaantonov/PycharmProjects/parser/chromedriver')
            browser.get('https://store.steampowered.com')

            # Время для логина в Steam ручками нужно делать, пока нет аккаунта без мобильной аутентификации
            time.sleep(25)

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

                # return None
                #
                # pages = browser.find_elements_by_class_name('market_paging_pagelink')
                # for page in pages[1:]:
                #     # print(page.text)
                #     page.click()
                #     time.sleep(1.51)
                #     soup = BeautifulSoup(browser.page_source, 'html.parser')
                #     markets_list += (soup.find_all('a', class_="market_listing_row_link"))



                card_min_price = 100
                card_set_link = ''
                card_set_price = 1000
                # markets_list.sort(key=by_price_key)




                # !!!!!!!!!!!!!
                # !!!!!!!!!!!!!
                # Для рублей переделать отбрасывание лишнего element_price
                # element_price = float(markets_element.find('span', class_='normal_price').span.text[1:-4]) #USD
                # element_price = float(markets_element.find('span', class_='normal_price').span.text[:-5].replace(',', '.'))  # RU

                # !!!!!!!!!!!!!
                # !!!!!!!!!!!!!



                for markets_element in markets_list:
                    element_type = markets_element.find('span', class_='market_listing_game_name').text

                    # element_price = float(markets_element.find('span', class_='normal_price').span.text[1:-4])  #USD
                    element_price = float(markets_element.find('span', class_='normal_price').span.text[:-5].replace(',', '.'))  # RU

                    if element_type == 'Набор карточек':
                        card_set_price = float(element_price)
                        card_set_link = markets_element['href']
                    if 'Коллекционная карточка' in element_type:
                        if card_min_price > element_price:
                            card_min_price = element_price
                    # print(
                    #     markets_element['href'],
                    #     markets_element.find('span', class_='normal_price').span.text[1:-4],
                    #     markets_element.find('span', class_='market_listing_item_name').text,
                    #     markets_element.find('span', class_='market_listing_game_name').text
                    # )
                # print(len(markets_list))

                if should_to_bye(card_min_price, card_set_price):
                    fw.write(card_set_link+'\t\n')
                    print(card_min_price, card_set_price)
                    result_card_sets.append(card_set_link)
            # Задержка перед выходом из браузера
            # time.sleep(500)
            browser.quit()
    return result_card_sets



print(parse())