#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-4
"""
用于设置request由哪个handler处理下载.
支援MultiDownloadHandler
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type



class MultiMiddleware():
    def __init__(self, settings):
        self.default_download_handler = settings.get('DEFAULT_DOWNLOAD_HANDLER', 'scrapy')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        request.meta.setdefault('download_handler', self.default_download_handler)
