#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-16
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type

#coding=utf8
#!/usr/bin/env python

from scrapy import log
from scrapy.core.downloader.handlers.http import HttpDownloadHandler as ScrapyDownloadHandler
from .requests_dh import RequestsDownloadHandler


class MultiDownloadHandler(object):
    def __init__(self, settings):
        self.default_download_handler = settings.get('DEFAULT_DOWNLOAD_HANDLER', 'scrapy')
        self.handlers = {
            'scrapy': ScrapyDownloadHandler(settings),
            'requests': RequestsDownloadHandler(settings)
        }

    def download_request(self, request, spider):
        handler_str = request.meta.setdefault('download_handler', self.default_download_handler)
        log.msg(format='use %(handler_str)s to open:%(request)s', level=log.DEBUG, spider=spider,
                handler_str=handler_str, request=request)
        handler = self.handlers[handler_str]
        defer = handler.download_request(request, spider)
        return defer
