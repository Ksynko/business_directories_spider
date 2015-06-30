# -*- coding: utf-8 -*-

# Scrapy settings for ie_business project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'ie_business'

SPIDER_MODULES = ['ie_business.spiders']
NEWSPIDER_MODULE = 'ie_business.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ie_business (+http://www.yourdomain.com)'

# Automatically slows down requests based on download times
AUTOTHROTTLE_ENABLED = True

HTTPCACHE_ENABLED = True
HTTPCACHE_DIR = '/home/ubuntu/data/golden'

ITEM_PIPELINES = {
#         'ie_business.pipelines.NameMatchPipeline': 400,
#         'ie_business.pipelines.StoragePipeline': 800,
        'ie_business.pipelines.MongoDBPipeline': 800,
        }

# Proxy rotation settings
# Retry many times since proxies often fail
RETRY_TIMES = 10
# Retry on most error codes since proxies fail for different reasons
RETRY_HTTP_CODES = [500, 503, 504, 400, 403, 404, 408]

DOWNLOADER_MIDDLEWARES = {
            'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware' : None,
            'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 100,
            'ie_business.utils.randomproxy.RandomProxy': 200,
            'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 300,
            'ie_business.utils.rotate_useragent.RotateUserAgentMiddleware': 400,
            'scrapy.contrib.spidermiddleware.referer.RefererMiddleware': 10
            }

# Proxy list containing entries like
# http://host1:port
# http://username:password@host2:port
# http://host3:port
#...
PROXY_LIST = '/home/ubuntu/proxylist.txt'

MONGODB_URI = 'mongodb://localhost:27017'
MONGODB_DB = "localpages"
MONGODB_COLLECTION = "localpages"
