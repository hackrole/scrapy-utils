#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-15
不需要,详见scrapy自带download handler
会自动计算content_length
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type


class ImmediateResponseMiddleware:
    def __init__(self, crawler):
        pass

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        pass

