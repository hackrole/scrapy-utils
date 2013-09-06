#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-4
"""
不需要,详见scrapy自带download handler
会自动计算host
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type

from urlparse import urlparse

class MoreBrowserMiddleware():
    def __init__(self,):
        pass

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_request(self, request, spider):
        #todo low 这里urlparse做缓存
        host = urlparse(request.url).hostname
        request.headers.setdefault('host', host)
