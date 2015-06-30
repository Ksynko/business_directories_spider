import os
from shutil import rmtree

from scrapy.utils.request import request_fingerprint
from settings import HTTPCACHE_DIR

def remove_data_from_cache(response, spider):
    key = request_fingerprint(response.request)
    path = os.path.join(HTTPCACHE_DIR, spider.name, key[0:2], key)
    rmtree(path)
