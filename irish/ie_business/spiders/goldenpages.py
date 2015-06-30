# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import ItemLoader

from ie_business.items import IeBusinessItem, IeBusinessLoader


class GoldenpagesLinkExtractor(LinkExtractor):

    """There is a bug in their pagination code which causes an endless loop; filtering the backward and forward
    links and just allowing the numbers will fix it"""

    def __init__(self):
        LinkExtractor.__init__(self, restrict_xpaths='//div[@id="paging-bottom"]')

    def extract_links(self, response):
        # The parent can do most of it for us
        links = LinkExtractor.extract_links(self, response)
        try:
            good_links = [link for link in links if link.text.isdigit()]
        except TypeError:
            return None

        return good_links

        

class GoldenpagesSpider(CrawlSpider):
    name = 'goldenpages'
    allowed_domains = ['goldenpages.ie']
    start_urls = ['http://www.goldenpages.ie/']

    rules = (
        Rule(LinkExtractor(allow=[r'ie\/\w*\-[\w\-]*\/', r'ie\/ms\/ms\/.*'], deny='\?refine=', restrict_xpaths='//div[@id="result-list"]'), callback='parse_item', follow=True),

        Rule(GoldenpagesLinkExtractor(), follow=True),
        # I *think* that these will go in order, so that the above will deal with navigation links
        # but still leave the below to deal with site category crawling; let's see
        Rule(LinkExtractor(restrict_xpaths='//div[@class="topic-block"]'), follow=True),

        Rule(LinkExtractor(restrict_xpaths='//div[@id="footer-content"]/ul/li[@class="footer-theme-li"]'), follow=True)
        

    )

    def parse_item(self, response):
        loader = IeBusinessLoader(item=IeBusinessItem(), response=response)
        loader.add_value('source', response.url)
        # These are the standard ones
        loader.add_xpath('name', '//meta[@property="og:title"]/@content')
        loader.add_xpath('business_type', '//meta[@property="og:type"]/@content')
        loader.add_xpath('url', '//meta[@property="og:url"]/@content')
        loader.add_xpath('address', '//meta[@property="og:street-address"]/@content')
        loader.add_xpath('latitude', '//meta[@property="og:latitude"]/@content')
        loader.add_xpath('longitude','//meta[@property="og:longitude"]/@content')
        loader.add_xpath('postal_code', '//meta[@property="og:postal-code"]/@content')
        loader.add_xpath('email', '//meta[@property="og:email"]/@content')
        loader.add_xpath('phone_number', '//meta[@property="og:phone_number"]/@content')
        loader.add_xpath('phone_number', '//div[@itemprop="telephone"]/text()')
        loader.add_xpath('fax_number',  '//meta[@property="og:fax_number"]/@content')
        loader.add_xpath('country', '//meta[@property="og:country-name"]/@content')
        # The ones where there is a special page for a business
        loader.add_xpath('country', '//span[@property="v:name"]/text()')
        # Presumably
        loader.add_value('business_type', 'company')
        # There must be a postcode?
        loader.add_xpath('url',  '//meta[@property="og:url"]/@content')
        loader.add_xpath('address', '//span[@property="v:street-address"]/text()')
        loader.add_xpath('website', '//a[@property="v:url"]/text()')
        loader.add_xpath('phone_number', '//span[@property="v:tel"]/text()')
        return loader.load_item()
