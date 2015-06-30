# -*- coding: utf-8 -*-

# Scrapy settings for uk project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'uk'

SPIDER_MODULES = ['uk.spiders']
NEWSPIDER_MODULE = 'uk.spiders'

ITEM_PIPELINES = {
             'uk.pipelines.DefaultFieldsPipeline': 200,
             'uk.pipelines.StoragePipeline': 300,
                }

AUTOTHROTTLE_ENABLED = True
# we should disable default Retry middleware
RETRY_ENABLED = False
UPDATED_RETRY_ENABLED = True

RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 408]
HTTPCACHE_IGNORE_HTTP_CODES = [403]
# HTTPCACHE_ENABLED = True
HTTPCACHE_DIR = '/tmp/cache_dir'
HTTPCACHE_EXPIRATION_SECS = 1209600
DOWNLOADER_MIDDLEWARES = {
            'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware' : None,
            'scrapyutils.randomproxy.RandomProxy': 200,
            'uk.middlewares.UpdatedRetryMiddleware': 150,
            'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 300,
            'scrapyutils.rotate_useragent.RotateUserAgentMiddleware': 400,
            }
import os
PROXY_LIST = os.getenv("HOME") + '/proxylist.txt'
UA_LIST = os.getenv("HOME") + '/user_agents.txt'
