# -*- coding: utf-8 -*-
import urlparse
import re

import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import ItemLoader
from scrapy.http import Request

from uk.items import UKBusinessItem


# this additional function can be used to get first element from XPath if it exist
cond_set_value = lambda y, default=0: y[0] if y else default

class ConstructionSpider(CrawlSpider):
    name = 'construction'
    allowed_domains = ['www.construction.co.uk']
    start_urls = ['http://www.construction.co.uk/']

    rules = (
        # http://www.construction.co.uk/directory.asp?dirtype=2
        Rule(LinkExtractor(allow=r'\/directory\.asp\?dirtype='), follow=True,
             callback='get_categories'),
    )

    def get_categories(self, response):
        # http://www.construction.co.uk/double-glazing-repairs/category_33.htm
        link_extractor = LinkExtractor(allow=r'\/category_\d+')
        links = link_extractor.extract_links(response)
        for link in links:
            category = link.text
            yield Request(url=link.url,
                          callback=self.get_companies_links_by_letter,
                          meta={'category':category})

    def get_companies_links_by_letter(self, response):
        # http://www.construction.co.uk/heating-contractors-and-consultants/22_A.htm
        letter_link_extractor = LinkExtractor(allow=r'\/\d+_[A-Z].htm')
        links_by_letter = letter_link_extractor.extract_links(response)
        if links_by_letter:
            for link in links_by_letter:
                yield Request(url=link.url,
                              callback=self.get_companies_links,
                              meta={'category': response.meta.get('category')})
        else:
            # there is no letters pagination at the page
            for request in self.get_companies_links(response):
                yield request

    def get_companies_links(self, response):
        companies_link_extractor = LinkExtractor(allow=r'\/company_\d{5,7}')
        companies_links = companies_link_extractor.extract_links(response)
        for link in companies_links:
            yield Request(url=link.url,
                          callback=self.parse_item,
                          # cookies=None,
                          meta={'category': response.meta.get('category')})

    def parse_item(self, response):
        il = ItemLoader(item=UKBusinessItem(), response=response)

        il.add_value('spider_name', unicode(self.name))
        il.add_xpath('name', '//td[@class="h1-listing-td"]/h1/text()')
        il.add_value('url', unicode(response.url))

        populated_dictionary = {
            'Company': u'',
            'Telephone': u'',
            'Address': u'',
            'Contact': u'',
            'Website': u'',
            'Mobile': u'',
            'Fax': u'',
        }
        tables = response.xpath('//table[@align="center"][@width="100%"]')
        email = u''
        zip_code = u''
        for table in tables:
            for tr in table.xpath('./tr'):
                td_text = cond_set_value(tr.xpath('./td[1]/text()').extract())
                if td_text in populated_dictionary.keys():
                    # replace will be used in case of address have
                    # link to map in brackets
                    populated_dictionary[td_text] = u' '.join(tr.xpath(
                        './td[2]/text()').extract()).replace('( )', '')
                if td_text == 'Website':
                    populated_dictionary['Website'] = cond_set_value(tr.xpath(
                        './td[2]/a/text()').extract())
                if td_text == 'Address':
                    guess_map_link = cond_set_value(tr.xpath(
                        './td/a/@href').extract())
                    if guess_map_link:
                        try:
                            # try get zip code from link to google_maps 
                            zip_code = urlparse.parse_qs(
                                urlparse.urlparse(
                                    guess_map_link).query)['q'][0]
                        except:
                            zip_code = u''
                if td_text == 'Email':
                    email_tr = tr
                    email_script = cond_set_value(tr.xpath(
                        './td/script/text()').extract())
                    try:
                        unstructered_email = cond_set_value(
                            re.findall(r"sw\('(.*)'\);", email_script))
                    except Exception as e:
                        print(e)
                        unstructered_email = u''
                    email = self.mail_parse_function(unstructered_email)


        il.add_value('phone_number', populated_dictionary['Telephone'])
        il.add_value('address', populated_dictionary['Address'])
        il.add_value('website', populated_dictionary['Website'])
        il.add_value('mobile_number', populated_dictionary['Mobile'])
        il.add_value('fax_number', populated_dictionary['Fax'])
        il.add_value('postal_code', zip_code)
        il.add_value('email', email)
        # sometimes next xpath may not found anything but category from meta
        # should save us
        il.add_xpath('category', '//td[@class="header"]/h1/text()')
        category = response.meta.get('category')
        if category:
            il.add_value('category', unicode(category))

        return il.load_item()

    def mail_parse_function(self, t):
        """This method perform same task as javascript sw()/job_sw()
        functions at the site."""
        t = t[:-4]
        stripped_part = '_yyz_'
        t = t.replace('.', '@')
        t = t.replace(stripped_part, '.')
        t = t[::-1]
        return t
