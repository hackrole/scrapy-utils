#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-15
不需要,详见scrapy自带download handler
会自动计算content_length
"""

from __future__ import division, print_function, unicode_literals
from scrapy import log
from feet8.utils.algorithm import get_text

__metaclass__ = type


class FirewallDetectorMiddleware:
    def __init__(self, crawler):
        settings = crawler.settings
        self.firewall_keywords = settings.get('FIREWALL_KEYWORDS', [])

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_response(self, request, response, spider):
        try:
            text = get_text(response.body_as_unicode())
        except Exception as e:
            return response
        for kw in self.firewall_keywords:
            if kw in text:
                log.msg('FirewallDetectorMiddleware:seems been blocked,kw:%s,below is text:\n%s' % (repr(kw), text))
        return response