#coding=utf8
#!/usr/bin/env python
"""
not used yet
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type

#Author:wuya @ smallteam
#Date: 13-5-13


from scrapy.spider import BaseSpider
from scrapy.http.request import Request


class Foot(BaseSpider):
    name = 'foot'

    def __init__(self, *args, **kwargs):
        super(Foot, self).__init__(*args, **kwargs)

    def init(self):
        raise NotImplementedError

    def get_item_list(self):
        raise NotImplementedError

    def parse_item_list(self, page):
        raise NotImplementedError

    def parse_item_detail(self, response):
        raise NotImplementedError

    def start_requests(self):
        self.init()
        item_list_pages = self.get_item_list()
        item_list = [self.parse_item_list(page) for page in item_list_pages]
        for item in item_list:
            detail_url = item.get('next_request')
            if detail_url:
                yield Request(detail_url, callback=self.parse_item_detail)
