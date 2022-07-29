import json

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider


class SearchPrices(Spider):
    name = 'get_prices'
    allowed_domains = ['steamcommunity.com', 'steamcardexchange.net']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/84.0.4147.135 Safari/537.36',
        'LOG_ENABLED': True
    }

    def start_requests(self):
        with open('appids.json', 'r') as f:
            data = json.load(f)



