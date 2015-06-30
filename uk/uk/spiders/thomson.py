# -*- coding: utf-8 -*-
from urllib import quote_plus
from urlparse import urljoin
import json

import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import ItemLoader
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy import log

from uk.items import UKBusinessItem
from uk.additional_tools import remove_data_from_cache


cond_set_value = lambda y, default=0: y[0] if y else default

class ThomsonSpider(CrawlSpider):
    name = 'thomson'
    allowed_domains = ['www.thomsonlocal.com']
    start_urls = ['http://www.thomsonlocal.com/']

    rules = (
        Rule(LinkExtractor(allow=r'\/popularsearches\/'), follow=True,
                           callback='parse_categories'),
    )

    pagination_pattern = 'http://www.thomsonlocal.com/Listing/AjaxSearch'\
        '?ResultOrder=advert_dist&Seed=&Location=uk&Phrase={prase}'\
        '&displayState=show&WhatTarget=&Page={page}&FilterTargets='
    pagination_headers = {
        'Accept': '*/*',
        'Content-Type': 'application/json;charset=UTF-8',
        'Content-Length': '93',
        'Accept-Encoding': 'gzip, deflate'
    }

    def error_handler(self, response):
        try:
            if 'We are sorry' in response.body:
                proxy = response.meta.get('proxy', '')
                r = response.request
                r.dont_filter = True
                r.meta.pop('proxy')
                try:
                    r.headers.pop('Proxy-Authorization')
                    remove_data_from_cache(response, self)
                except:
                    pass
                self.log('Request at url {0} with proxy {1} was failed'
                    ' due to country restriction access. Try resend this request'
                    ' with another proxy.'.format(response.url, proxy), log.INFO)
                return r
        except Exception as e:
            return None

    def parse(self, response):
        request_again = self.error_handler(response)
        if request_again:
            return request_again
        return super(ThomsonSpider, self).parse(response)

    def parse_categories(self, response):
        request_again = self.error_handler(response)
        if request_again:
            yield request_again
            return
        categories_extractor = LinkExtractor(
            restrict_xpaths='.//ul[@class="popTermsList"]')
        categories_links = categories_extractor.extract_links(response)
        for link in categories_links:
            yield Request(url=link.url, callback=self.get_items_and_pagination)
        letters_extractor = LinkExtractor(
            restrict_xpaths='.//div[@class="popTermsNavBar"]')
        letters_links = letters_extractor.extract_links(response)
        for link in letters_links:
            yield Request(url=link.url, callback=self.parse_categories)

    def get_items_and_pagination(self, response):
        request_again = self.error_handler(response)
        if request_again:
            yield request_again
            return
        items_extractor = LinkExtractor(deny=[r'\/image\/', r'\/map'],
                                        restrict_xpaths='.//div[@class="itemInfo"]/h2')
        items_links = items_extractor.extract_links(response)
        for link in items_links:
            yield Request(url=link.url, callback=self.parse_item)
        if response.xpath('.//a[@class="next"]').extract():
            total_quantity = response.xpath(
                '(.//div[@class="pageResults"]/span[@class="results"]'
                '/text()[normalize-space()])[2]').re(r'\d+')
            if total_quantity:
                total_quantity = int(total_quantity[0])
                pages = total_quantity/25
                page_range = range(1, pages+2)

            category = cond_set_value(response.xpath(
                './/input[@id="FrmWho"]/@value').extract())
            quoted_category = quote_plus(category)
            for page in page_range:
                next_url = self.pagination_pattern.format(prase=quoted_category,
                                                          page=page)
                yield Request(url=next_url, headers=self.pagination_headers,
                              dont_filter=True, method='POST',
                              callback=self.parse_pagination)

    def parse_pagination(self, response):
        request_again = self.error_handler(response)
        if request_again:
            yield request_again
            return
        data = json.loads(response.body)
        pagination = data['PaginationBar']
        res = data["Results"]
        s = Selector(text=res)
        links = s.xpath('.//div[@class="itemInfo"]/h2/a/@href').extract()
        for link in links:
            item_url = urljoin(self.start_urls[0], link)
            yield Request(url=item_url, callback=self.parse_item)

    def parse_item(self, response):
        request_again = self.error_handler(response)
        if request_again:
            return request_again
        il = ItemLoader(item=UKBusinessItem(), response=response)

        # From the OG section at the top
        il.add_xpath('name', '//meta[@property="og:title"]/@content')
        il.add_xpath('url', '//meta[@property="og:url"]/@content')
        il.add_xpath('latitude', '//meta[@property="og:latitude"]/@content')
        il.add_xpath('longitude', '//meta[@property="og:longitude"]/@content')
        il.add_xpath('address', '//meta[@property="og:street-address"]/@content')
        il.add_xpath('locality', '//meta[@property="og:locality"]/@content')
        il.add_xpath('postal_code', '//meta[@property="og:postal-code"]/@content')
        il.add_xpath('country', '//meta[@property="og:country-name"]/@content')

        # XPaths below are from the display
        il.add_xpath('name', '//span[@class="busname"]/text()')
        # No OG for this
        il.add_xpath('phone_number', '//span[@class="bustel"]/text()')
        il.add_xpath('website', '//a[@id="linkWebsite"]/@href')
        il.add_xpath('address', '//span[@data-yext="address.address"]/text()')
        il.add_xpath('locality', '//span[@itemprop="addressLocality"]/text()')
        il.add_xpath('postal_code', '//span[@itemprop="postalCode"]/text()')
        # Unicoded so it can share an input processor with the rest
        il.add_value('url', unicode(response.url))
        return il.load_item()
