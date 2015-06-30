# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from urlparse import parse_qs
from string import ascii_lowercase

import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import ItemLoader

from uk.items import UKBusinessItem


# this additional function can be used to get first element from XPath if it exist
cond_set_value = lambda y, default=0: y[0] if y else default

class BusinessMagnetSpider(CrawlSpider):
    name = 'business_magnet'
    allowed_domains = ['businessmagnet.co.uk']
    start_url_pattern = 'http://www.businessmagnet.co.uk/{0}.htm'
    start_urls = [start_url_pattern.format(letter) for letter in ascii_lowercase]
    start_urls.append(start_url_pattern.format('#'))

    rules = (
        Rule(LinkExtractor(
                allow=r'/company/',
                deny=[r'\/email']),
            follow=True,
            callback='parse_item'),

    )

    def parse_item(self, response):
        """Fields not populated by this method:
        locality, country, mobile_number, category.
        """
        il = ItemLoader(item=UKBusinessItem(), response=response)
        il.add_value('url', unicode(response.url))
        il.add_xpath('name', '//div[@class="company_details"]/h3/text()')

        address_p =response.xpath(
            '//div[@class="fl company_details_inset1"]/p')
        address_first_part = address_p.xpath(
            'text()[normalize-space()]').extract()
        address_first_part = [ad.strip().replace('\\n\\r', '') for ad
                             in address_first_part]
        address_second_part = cond_set_value(
            address_p.xpath(
                './/a[contains(@href, "town")]/text()').extract(), '')
        address = ', '.join(address_first_part) + ', '+ address_second_part
        if address == ', ':
            return
        il.add_value('address', address)

        postal_code = ''.join(
            address_p.xpath(
                './/a[not(contains(@href, "town"))]/text()').extract())
        il.add_value('postal_code', postal_code)

        il.add_xpath('website', './/div[@class="company-website "]/a/text()')
        il.add_xpath('fax_number', './/span[@class="company-fax"]/text()')
        il.add_xpath('phone_number', './/span[@class="company-phno"]/@phone')

        mail_a = response.xpath('.//a[@value="Contact us"]/text()').extract()
        try:
            mail_a.remove('Contact Us')
        except:
            pass
        mail_a = [a.strip() for a in mail_a]
        mail = '@'.join(mail_a)
        il.add_value('email', mail)

        latitude = ''
        longitude = ''
        map_data = cond_set_value(response.xpath(
            './/p[@class="direction_map"]/iframe/@src').extract())
        if map_data:
            try:
                qs = parse_qs(map_data)
                coordinates = qs['ll'][0].split(',')
                latitude = coordinates[0]
                longitude = coordinates[1]
            except:
                pass
        il.add_value('latitude', latitude)
        il.add_value('longitude', longitude)

        return il.load_item()
