import json

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider


# defino una clase que hereda de Spider

class SearchCards(Spider):
    name = 'search_cards'
    allowed_domains = ['steamcommunity.com']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/84.0.4147.135 Safari/537.36',
        'LOG_ENABLED': False  # Elimina los miles de logs que salen al ejecutar Scrapy en terminal
    }

    def start_requests(self):
        with open('game_test.json', 'r') as f:
            data = json.load(f)
            for game in data:
                yield scrapy.Request(
                    url='https://www.steamcardexchange.net/index.php?gamepage-appid-' + game['AppID'],
                    callback=self.parse)

    def parse(self, response, **kwargs):
        print('uwu')
        cards = response.xpath('//*[@id="content-area"]/div[2]/div[4]//d'
                               'iv[@class="showcase-element"]/div/a/@href').getall()
        for card in cards:
            print(card)


process = CrawlerProcess()
process.crawl(SearchCards)
process.start()  # the script will block here until the crawling is finished
