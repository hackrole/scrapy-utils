#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-18
"""
"""

from __future__ import division, print_function, unicode_literals
from scrapy.contrib.spidermiddleware.httperror import HttpError
from scrapy.exceptions import IgnoreRequest

__metaclass__ = type

from feet8.utils.hack import yield_item_through_bad_request
from scrapy import log


class ItemErrorSaveDownloaderMiddleware():
    ignore_errors = (HttpError, IgnoreRequest)

    def __init__(self, crawler):
        pass

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.ignore_errors):
            return
        item = request.meta.get('item', None)
        if not item:
            # debug
            # log.msg('ItemErrorSave filt:%s' % request.url)
            return
        else:
            doc = item['doc']
            doc['error_save'] = True
            #在这里没法获取到异常的traceback.还是只能看日志
            doc['error_dump'] = '%s:%s' % (str(exception.__class__), exception)
            # debug
            # log.msg('%s' % str(doc))
            log.msg('ItemErrorSaveDownloaderMiddleware,error:%s,try save item' % str(exception))
            return yield_item_through_bad_request(item)


class ItemErrorSaveSpiderMiddleware():
    ignore_errors = (HttpError, IgnoreRequest)

    def __init__(self, crawler):
        pass

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, self.ignore_errors):
            return
        item = response.meta.get('item', None)
        if not item:
            # debug
            # log.msg('ItemErrorSave filt:%s' % response.request.url)
            return
        else:
            doc = item['doc']
            doc['error_save'] = True
            #在这里没法获取到异常的traceback.还是只能看日志
            doc['error_dump'] = '%s:%s' % (str(exception.__class__), exception)
            # debug
            # log.msg('%s'%str(doc))
            log.msg('ItemErrorSaveSpiderMiddleware,error:%s,try save item' % str(exception))
            yield item


