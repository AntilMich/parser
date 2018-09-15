import requests
import re



resp = requests.get('https://steamcommunity.com/market/listings/730/Horizon%20Case')
item_nameid = re.search(r'Market_LoadOrderSpread\( \d+ \)', resp.text).group()[24:-2]

# response = requests.get('https://steamcommunity.com/market/itemordershistogram?country=RU&language=russian&currency=5&item_nameid=' + item_nameid + '&two_factor=0')
# json = response.json()
#
# for key in json:
#     print(key, json[key])