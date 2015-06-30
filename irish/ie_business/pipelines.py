# -*- coding: utf-8 -*-
import logging

import requests
from scrapy import log
from pymongo import MongoClient

# from matcher import Matcher

client = MongoClient()
businesses_collection = client.ie_business.businesses
irish_companies_collection = client.cro.companies

def strip_limited(string):
    string = string.lower().strip()
    if string[-7:] == 'limited':
        string = string[0:-7]
    return string

class NameMatchPipeline(object):
    """Try to match against the CRO API"""
    def process_item(self, item, spider):
        params = {'alpha': item['name']}
        match_result = requests.get('http://localhost:8000/cro/companies/search/', params=params)
        # The match results are actually full Irish companies; may as well save them to avoid repeatedly
        # hitting CRO
        for result in match_result.json():
            irish_companies_collection.update(
                    {'company_num': result['company_num']}, 
                    result, 
                    upsert=True)
        
        try:
            best_match_score = 0
            for result in match_result.json():
                matcher = Matcher(item['name'], result['company_name'])
                score = matcher.get_similarity_ratio()
                if score > best_match_score:
                    best_match_score = score
                    best_match = result

            item['company_number'] = best_match['company_num']
            item['company_name'] = best_match['company_name']

            item['match_distance'] = best_match_score
            log.msg("Business %s matched to %s, distance %s" % (item['name'], best_match['company_name'], item['match_distance']))
        except UnboundLocalError:
            log.msg("No match found")
            # No match at all found
            pass


        return item

class StoragePipeline(object):
    """Store the results in the database"""
    def process_item(self, item, spider):
        businesses_collection.insert(dict(item))
        return item


class MongoDBPipeline(object):
    """Store items to MongoDB"""
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        pipeline.mongodb_uri = crawler.settings.get("MONGODB_URI", "mongodb://localhost:27017")
        pipeline.mongodb_db = crawler.settings.get("MONGODB_DB", "ie_business")
        pipeline.mongodb_col = crawler.settings.get("MONGODB_COLLECTION", "localpages")
        return pipeline

    def __init__(self):
        self.mdb = None

    def open_spider(self, spider):
        self.mdb = getattr(MongoClient(self.mongodb_uri), self.mongodb_db)


    def process_item(self, item, spider):
        getattr(self.mdb, self.mongodb_col).update({"url": item["url"]}, dict(item), upsert=True)
        return item
