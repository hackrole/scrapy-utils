#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-10
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
        immediate_response = request.meta.get('immediate_response', None)
        if immediate_response:
            return immediate_response
