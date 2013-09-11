#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-18
"""
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type

from scrapy.http.request import Request


def yield_item_through_bad_request(item):
    def _errback(error):
        request = error.request
        items = request.meta['items']
        for item in items:
            yield item
    meta = {'item': item}
    req = Request('http:', callback=_errback, errback=_errback, meta=meta, dont_filter=True)
    return req
