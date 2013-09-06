#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-17
"""

from __future__ import division, print_function, unicode_literals
from scrapy.contrib.downloadermiddleware.chunked import ChunkedTransferMiddleware as ScrapyChunkedTransferMiddleware

__metaclass__ = type


class ChunkedTransferMiddleware(ScrapyChunkedTransferMiddleware):
    """This middleware adds support for chunked transfer encoding, as
    documented in: http://en.wikipedia.org/wiki/Chunked_transfer_encoding
    """

    def process_response(self, request, response, spider):
        if request.meta.get('download_handler', 'scrapy') == 'scrapy':
            return super(ChunkedTransferMiddleware, self).process_response(request, response, spider)
        return response
