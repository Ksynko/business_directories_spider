# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import ItemLoader
from scrapy.http import Request

from uk.items import UKBusinessItem


# this additional function can be used to get first element from XPath if it exist
cond_set_value = lambda y, default=0: y[0] if y else default

class BizWikiSpider(CrawlSpider):
    name = 'bizwiki'
    allowed_domains = ['bizwiki.co.uk']
    start_urls = ['http://www.bizwiki.co.uk/']

    rules = (
        # Rule for company links
        # /accounting-services/1644775/taxassist-accountants.htm
        Rule(LinkExtractor(
                allow=r'\/\d+\/.*\.htm'),
            follow=True,
            callback='parse_item'),

        # Rule for categories from main page
        # http://www.bizwiki.co.uk/curtains.htm
        # and also for compalies by location
        # http://www.bizwiki.co.uk/curtains/aberdeenshire/aberdeen.htm
        Rule(LinkExtractor(
                allow=r'\.htm',
                deny=[r'\/about\.htm', r'\/bizwikibot\.htm', r'\/faq\.htm',
                      r'\/policies\.htm', r'\/terms\.htm', r'\/privacy\.htm',
                      r'\/disclaimer\.htm', r'\/contact\.htm',
                      r'\/\d+\/.*\.htm']),
            follow=True),
    )

    def parse_item(self, response):
        """This method will not populate such fields:
        locality, mobile_number, country, email
        """
        il = ItemLoader(item=UKBusinessItem(), response=response)

        il.add_value('url', unicode(response.url))
        il.add_xpath('name', '//h3[@class="biz"]/text()')
        il.add_xpath('category', '//div[@id="breadcrumbs"]/a[2]/text()')

        bcon_list = response.xpath('//ul[@class="bcon"]/li')
        for li in bcon_list:
            li_text = cond_set_value(li.xpath('.//b/text()').extract())
            if li_text == 'Tel:':
                phone_number = cond_set_value(li.xpath('text()').extract())
                il.add_value('phone_number', phone_number)
            if li_text == 'Web:':
                website = cond_set_value(li.xpath('.//a/text()').extract())
                il.add_value('website', website)
            if li_text == 'Fax:':
                fax_number = cond_set_value(li.xpath('text()').extract())
                il.add_value('fax_number', fax_number)

        address_list = response.xpath('//ul[@class="bad"]/li/text()').extract()
        if address_list:
            address_without_postal_code = u', '.join(address_list[:-1])
            postal_code = address_list[-1]
            il.add_value('address', address_without_postal_code)
            il.add_value('postal_code', postal_code)

        il.add_xpath('latitude', '//div[@id="lat"]/text()')
        il.add_xpath('longitude', '//div[@id="lng"]/text()')

        return il.load_item()
