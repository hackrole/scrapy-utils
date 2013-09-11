#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-18
"""
"""

from __future__ import division, print_function, unicode_literals
from scrapy.exceptions import IgnoreRequest
from scrapy import log
from scrapy.http.request import Request

__metaclass__ = type



# class DupfilterMiddleware():
#
#     def __init__(self, crawler):
#         pass
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         return cls(crawler)
#
#     def process_request(self, request, spider):
#         if request.dont_filter:
#             return
#         result = spider.is_duplicate_request(request)
#         if result:
#             raise IgnoreRequest('DupfilterMiddleware,duplicate request:%s' % request.url)


class DupfilterMiddleware(object):

    def __init__(self, crawler):
        pass

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_spider_output(self, response, result, spider):
        for x in result:
            if isinstance(x, Request):
                if x.dont_filter:
                    yield x
                else:
                    result = spider.is_duplicate_request(x)
                    if result:
                        log.msg(format='DupfilterMiddleware,duplicate request:%(request)s',
                                level=log.DEBUG, spider=spider, request=x)
                    else:
                        yield x
            else:
                yield x

