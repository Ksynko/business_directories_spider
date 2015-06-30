# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from uk.items import UKBusinessItem



class YellSpider(CrawlSpider):
    name = "yell"
    allowed_domains = ["www.yell.com"]
    start_urls = (
            'http://www.yell.com/',
    )

    rules = (
        Rule(LinkExtractor(allow=[r'/biz/']), callback='parse_item', follow=True),

        Rule(LinkExtractor(), follow=True),

    )


    def parse_item(self, response):
        import pdb; pdb.set_trace()
        i['name'] = response.xpath('//h1[@class="m-business-card--name"]/text()').extract()[0]
        i['postal_code'] = response.xpath('//span[@itemprop="postalCode"]/text()').extract()[0]
        i['street_address'] = response.xpath('//span[@itemprop="streetAddress"]/text()').extract()[0]
        i['address_locality'] = response.xpath('//span[@itemprop="addressLocality"]/text()').extract()[0]
        i['phone_number'] = response.xpath('//span[@itemprop="addressLocality"]/text()').extract()[0]
        return item
