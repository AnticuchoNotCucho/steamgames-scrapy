import json
import scrapy
from pymongo import MongoClient
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider


def cleandata(text):
    new_text = text.replace('[', '').replace(']', '').replace("'", '').replace('https://steamcommunity.com/market'
                                                                               '/listings/753/', '')
    return new_text


# defino una clase que hereda de Spider
class SearchCards(Spider):
    name = 'search_cards'
    # inicializo el mongo cliente
    client = MongoClient('localhost', 27017)
    db = client['profit']
    collection = db['cards']

    allowed_domains = ['steamcommunity.com']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/84.0.4147.135 Safari/537.36',
        'LOG_ENABLED': False  # Elimina los miles de logs que salen al ejecutar Scrapy en terminal
    }

    # Generamos url en base a las appids de cada juego almacenado en la base de datos
    def start_requests(self):
        games = self.db['games']
        for game in games.find():
            yield scrapy.Request(
                url='https://www.steamcardexchange.net/index.php?gamepage-appid-' + game['AppID'],
                callback=self.parse, meta={'game': game['AppID']})

    # Parseamos la pagina de cada juego
    def parse(self, response, **kwargs):
        cards = response.xpath('//*[@id="content-area"]/div[2]/div[4]//d'
                               'iv[@class="showcase-element"]/div/a/@href').getall()
        # por cada link de cromo, almacenamos su hash_name y appid
        for card in cards:
            card = cleandata(card)
            game = response.meta['game']
            collection = self.db['cards']
            collection.insert_one({'_id': card, 'game_id': game, 'hash_name': card})
        print('Cards added to database')


# nos permite ejecutar el programa desde el main sin necesidad de ejecutar scrapy.py
process = CrawlerProcess()
process.crawl(SearchCards)
process.start()
