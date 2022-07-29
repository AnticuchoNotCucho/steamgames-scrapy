import json
import scrapy
from pymongo import MongoClient
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider


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

    # Generamos url en base a las appids de cada juego almacenado en el json
    def start_requests(self):
        with open('games.json', 'r') as f:
            data = json.load(f)
            for game in data:
                yield scrapy.Request(
                    url='https://www.steamcardexchange.net/index.php?gamepage-appid-' + game['AppID'],
                    callback=self.parse, meta={'game': game['AppID']})

    def parse(self, response, **kwargs):
        cards = response.xpath('//*[@id="content-area"]/div[2]/div[4]//d'
                               'iv[@class="showcase-element"]/div/a/@href').getall()
        for card in cards:
            game = response.meta['game']
            collection = self.db['cards']
            collection.insert_one({'game_id': game, 'hash_name': card})


process = CrawlerProcess()
process.crawl(SearchCards)
process.start()  # the script will block here until the crawling is finished
