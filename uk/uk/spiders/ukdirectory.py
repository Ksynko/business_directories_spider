# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from urlparse import urljoin
from string import ascii_lowercase

import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import ItemLoader
from scrapy.http import Request

from uk.items import UKBusinessItem


# this additional function can be used to get first element from XPath if it exist
cond_set_value = lambda y, default=0: y[0] if y else default

class UKDirectorySpider(CrawlSpider):
    name = 'uk_directory'
    allowed_domains = ['ukdirectory.co.uk']
    start_urls = ['http://www.ukdirectory.co.uk/']

    rules = (
        Rule(LinkExtractor(
                restrict_xpaths='.//div[not(contains(@class, '\
                    '"featuredLocation"))]/h2[@class="categoryHeader"]'),
            follow=True,
            callback='parse_categories'),
    )

    def parse_categories(self, response):
        l = LinkExtractor(
            restrict_xpaths='.//div[@class="categoryListContainer"]')
        links = l.extract_links(response)
        for link in links:
            yield Request(url=link.url, callback=self.parse_items_links)

    def parse_items_links(self, response):
        categories_links_extractor = LinkExtractor(
            restrict_xpaths='.//div[@class="categoryListContainer"]')
        cat_links = categories_links_extractor.extract_links(response)
        for link in cat_links:
            yield Request(url=link.url, callback=self.parse_items_links)

        items_links_extractor = LinkExtractor(
            restrict_xpaths='.//div[@class="directory-listing"]/h3')
        items_links = items_links_extractor.extract_links(response)
        for link in items_links:
            yield Request(url=link.url, callback=self.parse_item)

        pagination_link = cond_set_value(
            response.xpath('.//a[@class="more"]/@href').extract())
        if pagination_link:
            full_pagination_link = urljoin(self.start_urls[0],
                                           pagination_link)
            yield Request(url=full_pagination_link,
                          callback=self.parse_items_links)

    def parse_item(self, response):
        """Fields not populated by this method:
        email, mobile_number, latitude, longitude.
        """
        il = ItemLoader(item=UKBusinessItem(), response=response)
        il.add_value('url', unicode(response.url))
        il.add_xpath('name',
            './/h1[@class="title"]/a/text() | .//h1[@class="title"]/text()')

        address_text = response.xpath(
            './/address/text()[normalize-space()]').extract()
        address_text = [part.strip().rstrip(',') for part in address_text]
        address = ', '.join(address_text)
        il.add_value('address', address)

        il.add_xpath('postal_code', './/h3[@class="postcode"]/text()')
        il.add_xpath('website',
            './/div[@class="contact-info"]//strong/a/@href |'
            './/div[@class="contact-info"]/ul/strong/span/text()')
        il.add_xpath('category',
            './/ul[contains(@class, "breadcrumb")]/li[last()]/a/text()')
        il.add_xpath('linkedin',
            './/ul[contains(@class, "social")]/li[@class="linkedIn"]/a/@href')
        il.add_xpath('description',
            './/div[@class="about-text"]/p/text()')

        phones_sp = response.xpath('.//div[@class="contact-info"]//li/span')
        for span in phones_sp:
            text = cond_set_value(
                span.xpath('text()[normalize-space()]').extract(), '')
            if 'T:' in text:
                phone_number = cond_set_value(
                    span.xpath('.//div/text()').extract())
                il.add_value('phone_number', phone_number)
            if 'F:' in text:
                fax_number = cond_set_value(
                    span.xpath('.//div/text()').extract())
                il.add_value('fax_number', fax_number)

        return il.load_item()
