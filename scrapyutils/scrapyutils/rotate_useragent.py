#!/usr/bin/python
#-*-coding:utf-8-*-

import random
from scrapy.contrib.downloadermiddleware.useragent import UserAgentMiddleware


class RotateUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, settings, user_agent=''):
        with open(settings.get('UA_LIST'), 'r') as f:
            self.user_agent_list = [x.strip('\n') for x in f.readlines()]

    @classmethod
    def from_crawler(cls, crawler):
        # with open(crawler.settings.get('UA_LIST'), 'r') as f:
        #     self.user_agent_list = [x.strip('\n') for x in f.readlines()]
        # import pdb; pdb.set_trace()
        return cls(crawler.settings)

    def process_request(self, request, spider):
        ua = random.choice(self.user_agent_list)
        if ua:
            request.headers.setdefault('User-Agent', ua)

