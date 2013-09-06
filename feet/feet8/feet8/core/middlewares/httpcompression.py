#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-17
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type

from scrapy.contrib.downloadermiddleware.httpcompression import HttpCompressionMiddleware as ScrapyHttpCompressionMiddleware


class HttpCompressionMiddleware(ScrapyHttpCompressionMiddleware):
    """This middleware allows compressed (gzip, deflate) traffic to be
    sent/received from web sites"""

    def process_request(self, request, spider):
        if request.meta.get('download_handler', 'scrapy') == 'scrapy':
            return super(HttpCompressionMiddleware, self).process_request(request, spider)

    def process_response(self, request, response, spider):
        if request.meta.get('download_handler', 'scrapy') == 'scrapy':
            return super(HttpCompressionMiddleware, self).process_response(request, response, spider)
        return response
