#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-10
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type


class PriorityMiddleware:
    def __init__(self, crawler):
        settings = crawler.settings
        self.priorities = settings.get('PRIORITIES', {})

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        request_type = request.meta.get('request_type', None)
        if not request_type:
            return
        priority = self.priorities.get(request_type, 0)
        request.priority += priority
