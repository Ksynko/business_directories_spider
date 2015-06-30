# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import ItemLoader
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url
from scrapy.utils.python import unique as unique_list
from ie_business.items import IeBusinessItem, IeBusinessLoader


class LocalpagesLinkExtractor(LinkExtractor):
    def extract_links(self, response):
        html = Selector(response)
        try:
            base_url = response.xpath("//base/@href").extract()[0]
        except IndexError:
            base_url = get_base_url(response)
        if self.restrict_xpaths:
            docs = [subdoc
                    for x in self.restrict_xpaths
                    for subdoc in html.xpath(x)]
        else:
            docs = [html]
        all_links = []
        for doc in docs:
            links = self._extract_links(doc, response.url, response.encoding, base_url)
            all_links.extend(self._process_links(links))
        return unique_list(all_links)

class LocalpagesSpider(CrawlSpider):
    name = 'localpages'
    allowed_domains = ['localpages.ie']
    start_urls = ['http://www.localpages.ie/']

    rules = (
        # They seem to be mainly 6 figures, but just to be sure:
        Rule(LocalpagesLinkExtractor(allow=[r'[0-9]{5,7}\/'], deny=[r'\/counties\/', 'AddBusiness']), callback='parse_item', follow=True),
        Rule(LocalpagesLinkExtractor(allow=[r'\/categories\/', r'\/Categories\/']), follow=True),
    )

    def parse_item(self, response):
        loader = IeBusinessLoader(item=IeBusinessItem(), response=response)
        loader.add_value('source', self.name)
        # These are the standard ones
        loader.add_xpath('name', '//td[@itemprop="name"]/text()')
        loader.add_xpath('business_type', '//meta[@property="og:type"]/@content')
        loader.add_value('url', response.url)
        loader.add_xpath('address', '//td[text()="Address:"]/following-sibling::td[1]/text()')
        loader.add_xpath('address', '//td[@itemprop="location"]/text()')
        loader.add_xpath('latitude', '//script', re="Latitude\"\s*:\s*([\d\-\.]+)")
        loader.add_xpath('longitude','//script', re="Longitude\"\s*:\s*([\d\-\.]+)")
        # loader.add_xpath('postal_code', '//meta[@property="og:postal-code"]/@content')
        # loader.add_xpath('email', '//meta[@property="og:email"]/@content')
        loader.add_xpath('phone_number', '//td[@itemprop="phone"]/text()')
        # loader.add_xpath('fax_number',  '//meta[@property="og:fax_number"]/@content')
        # loader.add_xpath('country', '//meta[@property="og:country-name"]/@content')
        # The ones where there is a special page for a business
        # loader.add_xpath('country', '//span[@property="v:name"]/text()')
        # Presumably
        loader.add_value('business_type', 'company')
        # There must be a postcode?
        # loader.add_xpath('url',  '//meta[@property="og:url"]/@content')
        # loader.add_xpath('address', '//span[@property="v:street-address"]/text()')
        loader.add_xpath('website', '//td[text()="Web:"]/following-sibling::td[1]/a/text()')
        # loader.add_xpath('phone_number', '//span[@property="v:tel"]/text()')
        return loader.load_item()
