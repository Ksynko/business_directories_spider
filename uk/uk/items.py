# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.contrib.loader.processor import TakeFirst, MapCompose

class StripFirstField(scrapy.Field):
    """Just to save doing the unicode strip and TakeFirst each time"""
    def __init__(self):
        super(StripFirstField, self).__init__(
            input_processor=MapCompose(unicode.strip),
            output_processor=TakeFirst()
            )
        pass

def filter_space_and_hyphens(value):
    value = value.replace(' ', '').replace('-', '')
    return value

class StripSpacesAndHyphensField(scrapy.Field):
    """Strip spaces and hyphens from numbers and postal codes"""
    def __init__(self):
        super(StripSpacesAndHyphensField, self).__init__(
            input_processor=MapCompose(unicode.strip,
                filter_space_and_hyphens),
            output_processor=TakeFirst()
            )

class UKBusinessItem(scrapy.Item):
    source = StripFirstField()
    name = StripFirstField()
    # business_type = scrapy.Field()
    # The canonical URL
    url = scrapy.Field(
            input_processor=MapCompose(unicode.strip),
            output_processor=TakeFirst()
            )
    address = StripFirstField()
    locality = StripFirstField()
    latitude = StripFirstField()
    longitude = StripFirstField()
    postal_code = StripSpacesAndHyphensField()
    phone_number = StripSpacesAndHyphensField()
    country = StripFirstField()
    website = StripFirstField()
    mobile_number = StripSpacesAndHyphensField()
    fax_number = StripSpacesAndHyphensField()
    email = StripFirstField()
    category = StripFirstField()
    updated = scrapy.Field()
    linkedin = StripFirstField()
    description = StripFirstField()
    pass
