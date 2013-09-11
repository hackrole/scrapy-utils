#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-19
"""
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type

# This recipe was taken from the old wiki.
# 
# You can make Scrapy send HTTP/1.1 requests by overriding the Scrapy HTTP Client Factory, with the following (undocumented) setting:
# 
#     DOWNLOADER_HTTPCLIENTFACTORY = 'myproject.downloader.HTTPClientFactory'

from scrapy.core.downloader.webclient import ScrapyHTTPClientFactory, ScrapyHTTPPageGetter

class PageGetter(ScrapyHTTPPageGetter):

    def sendCommand(self, command, path):
        self.transport.write(b'%s %s HTTP/1.1\r\n' % (command, path))

class HTTPClientFactory(ScrapyHTTPClientFactory):

     protocol = PageGetter

# Snippet imported from snippets.scrapy.org (which no longer works)
# author: pablo
# date  : Sep 16, 2011
