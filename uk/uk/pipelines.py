# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime

from pymongo import MongoClient
client = MongoClient()
uk_businesses_collection = client.uk_business.businesses

class StoragePipeline(object):
    """Store the results in the database"""
    def process_item(self, item, spider):
        uk_businesses_collection.update({'url': item['url']}, dict(item), upsert=True)
        return item

class DefaultFieldsPipeline(object):
    """Populate items fields with default values"""
    def process_item(self, item, spider):
        item['updated'] = unicode(datetime.datetime.now())
        item['source'] = unicode(spider.name)
        return item