import json
import scrapy
from pymongo import MongoClient
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider


class SearchPrices(Spider):
    name = 'get_prices'
    # inicializo el mongo cliente
    client = MongoClient('localhost', 27017)
    db = client['profit']
    list_games = []
    allowed_domains = ['steamcommunity.com']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/84.0.4147.135 Safari/537.36',
        'LOG_ENABLED': True,
        'LOG_LEVEL': 'INFO',
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 0.5,
    }

    # generamos lista de juegos para iterar sobre ellos
    # def generate_list(self):
    #   games = self.db['games']
    #   for game in games.find():
    #       game_id = game['AppID']
    #       game_title = game['Title']
    #      self.list_games.append([game_id, game_title])

    # comenzamos la iteracion en los links de los cromos
    def start_requests(self):
        games = self.db['games']
        for game in games.find():
            cards = self.db['cards']
            card_list = cards.find({'game_id': game['AppID']})
            for card in card_list:
                yield scrapy.Request(
                    url='https://steamcommunity.com/market/priceoverview/?appid=753&currency=34&market_hash_name=' +
                        card['hash_name']
                    , callback=self.parse, meta={'game': game, 'card': card})

    # parseamos la respuesta de cada cromo y almacenamos los precios en la base de datos
    def parse(self, response, **kwargs):
        game = response.meta['game']
        card = response.meta['card']
        response_json = json.loads(response.body)
        lowest_price = response_json['lowest_price']
        median_price = response_json['median_price']
        collection = self.db['cards_prices']
        collection.insert_one({'hash_name': card['hash_name'],
                               'game_title': game['Title'],
                               'lowest_price': lowest_price,
                               'median_price': median_price})


process = CrawlerProcess()
process.crawl(SearchPrices)
process.start()
