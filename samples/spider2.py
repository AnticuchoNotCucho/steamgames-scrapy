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
        'USER_AGENTS': [
            ('Mozilla/5.0 (X11; Linux x86_64) '
             'AppleWebKit/537.36 (KHTML, like Gecko) '
             'Chrome/57.0.2987.110 '
             'Safari/537.36'),  # chrome
            ('Mozilla/5.0 (X11; Linux x86_64) '
             'AppleWebKit/537.36 (KHTML, like Gecko) '
             'Chrome/61.0.3163.79 '
             'Safari/537.36'),  # chrome
            ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) '
             'Gecko/20100101 '
             'Firefox/55.0')  # firefox
        ],
        'LOG_ENABLED': True,
        'LOG_LEVEL': 'INFO',
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 0.5,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_useragents.downloadermiddlewares.useragents.UserAgentsMiddleware': 500,
        },
    }

    # comenzamos la iteracion en los links de los cromos
    def start_requests(self):
        games = self.db['games']
        for game in games.find():
            cards = self.db['cards']
            card_list = cards.find({'game_id': game['AppID']})
            for card in card_list:
                print(card['hash_name'])
                yield scrapy.Request(
                    url='https://steamcommunity.com/market/priceoverview/?appid=753&currency=34&market_hash_name=' +
                        card['hash_name']
                    , callback=self.parse, meta={'game': game, 'card': card}, errback=self.errback)

    # En caso de error 500 o alguno similar, almacenamos la carta sin precio y continuamos.
    def errback(self, failure):
        print(failure)
        game = failure.request.meta['game']
        card = failure.request.meta['card']
        collection = self.db['cards_prices']
        collection.insert_one({'hash_name': card['hash_name'],
                               'game_title': game['Title'],
                               'lowest_price': 'N/A',
                               'median_price': 'N/A'})
        print('Card added to database')

    # parseamos la respuesta de cada cromo y almacenamos los precios en la base de datos
    def parse(self, response, **kwargs):
        game = response.meta['game']
        card = response.meta['card']
        response_json = json.loads(response.body)
        lowest_price = response_json['lowest_price']
        median_price = response_json['median_price']
        if response_json['success']:
            try:
                collection = self.db['cards_prices']
                collection.insert_one({'hash_name': card['hash_name'],
                                       'game_title': game['Title'],
                                       'lowest_price': lowest_price,
                                       'median_price': median_price})
                print('Card added to database')
                print(card['hash_name'])
            except Exception as e:
                print(e)


process = CrawlerProcess()
process.crawl(SearchPrices)
process.start()
