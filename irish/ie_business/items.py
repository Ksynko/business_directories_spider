# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst


class IeBusinessLoader(ItemLoader):
  
    default_output_processor = TakeFirst()


class IeBusinessItem(scrapy.Item):
    # Where this particular item came from. Eg 'localpages', 'goldenpages'
    # Name of the spider is probably fine
    source = scrapy.Field()
    # The name of the business
    name = scrapy.Field()
    # Not used on most sites apart from Golden Pages; leave blank
    business_type = scrapy.Field()
    # The canonical URL for this record; generally just the url it was scraped
    # from 
    url = scrapy.Field()
    # Should be obvious
    address = scrapy.Field()
    # Only if the site itself provides it, otherwise leave blank
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    # Ireland doesn't actually have postal codes. Blank unless the site
    # specifically provides it
    postal_code = scrapy.Field()
    email = scrapy.Field()
    phone_number = scrapy.Field()
    fax_number = scrapy.Field()
    # Only if the site provides
    country = scrapy.Field()
    # The actual website for the company. For example http://www.goldenpages.ie/videnda-distribution-ltd-dublin-D24/1/
    # -> www.videnda.ie
    website = scrapy.Field()
    # -----------------------
    # Ignore the below for now
    # This is added in post processing pipeline
    company_number = scrapy.Field()
    # This is added in post processing pipeline
    company_name = scrapy.Field()
    # Levenshtein distance based on how close the match was
    match_distance = scrapy.Field()

