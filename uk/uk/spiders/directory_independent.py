# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import ItemLoader

from uk.items import UKBusinessItem


# this additional function can be used to get first element from XPath if it exist
cond_set_value = lambda y, default=0: y[0] if y else default

class DirectoryIndependentSpider(CrawlSpider):
    name = 'directory_independent'
    allowed_domains = ['directory.independent.co.uk']
    start_urls = ['http://directory.independent.co.uk/']

    rules = (
        # Rule fo categories from main page
        Rule(LinkExtractor(
                allow=r'directory',
                deny=[r'\/company\/', r'\/map', r'\/network', r'\/about-us',
                      r'\/privacy-policy', r'\/cookie-policy',
                      r'\/terms-conditions', r'\/contact-us',
                      r'\/add-listing', r'\/tel:\d+', r'\/claim-listing']),
            follow=True),
        # Rule for companies links
        # http://directory.independent.co.uk/company/shoreditch-locksmith-e2/16639134
        Rule(LinkExtractor(
                allow=r'/company/.*/\d+',
                deny=[r'\/email']),
            follow=True,
            callback='parse_item'),
        # Rule for pagination
        # http://directory.independent.co.uk/auto-locksmith/in/uk?page=2
        Rule(LinkExtractor(allow=r'uk\?page=\d+'), follow=True)
    )

    def parse_item(self, response):
        """Fields not populated by this method:
        locality, country, fax_number, email.
        """
        il = ItemLoader(item=UKBusinessItem(), response=response)
        il.add_value('source', unicode(self.name))

        il.add_xpath('name', '//h2[@class="profile-heading"]/text()')
        il.add_value('url', unicode(response.url))

        full_address = response.xpath(
            '//p[@class="profile-address"]/text()').extract()
        address_without_zip = u' '.join(full_address[:-1])
        try:
            postal_code = unicode(full_address[-1])
        except:
            # this mean no any address at the page
            postal_code = u''
        il.add_value('address', address_without_zip)
        il.add_value('postal_code', postal_code)

        il.add_xpath('website', '//p[@class="profile-link"]/a/@href')
        il.add_xpath('category',
            '//div[@class="form-group"]'
            '/div[@class="input-group"]/input/@value')

        mobile_number = u''
        phone_number = u''
        profile_number = response.xpath('//p[@class="profile-number "]')
        if profile_number.xpath('text()').re('Mobile'):
            mobile_number = cond_set_value(
                profile_number.xpath('./a/@val').extract())
        else:
            phone_number = cond_set_value(
                profile_number.xpath('./a/@val').extract())

        secondary_number = response.xpath(
            '//p[contains(@class, "profile-number-secondary")]')
        secondary_number_is_mobile = secondary_number.xpath(
            'text()').re('Mobile')
        if secondary_number_is_mobile:
            mobile_number = cond_set_value(
                secondary_number.xpath('./a/@val').extract())
        if not secondary_number_is_mobile and not phone_number:
            phone_number = cond_set_value(
                secondary_number.xpath('./a/@val').extract())
        il.add_value('mobile_number', unicode(mobile_number))
        il.add_value('phone_number', unicode(phone_number))

        latitude = u''
        longitude = u''
        coordinates = cond_set_value(
            re.findall(r'createStandardMarker\((.*)\{brush', response.body))
        if coordinates:
            lat_and_long = [coord.strip() for coord in
                            coordinates.strip().split(',')]
            if len(lat_and_long) >= 2:
                latitude = unicode(lat_and_long[0])
                longitude = unicode(lat_and_long[1])
        il.add_value('latitude', latitude)
        il.add_value('longitude', longitude)

        return il.load_item()
