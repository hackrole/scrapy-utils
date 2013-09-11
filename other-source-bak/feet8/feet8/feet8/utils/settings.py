#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-11
"""

from __future__ import division, print_function, unicode_literals
import os

__metaclass__ = type
import copy


def import_spider_global_settings(package, name):
    try:
        path = '%s.settings' % package
        base_mod = __import__(path, {}, {}, [''])
        mod = __import__(name, {}, {}, [''])
        for k, v in base_mod.__dict__.items():
            if k.startswith('__'):
                continue
            mod.__dict__[k] = copy.copy(v)
    except Exception as e:
        pass


def use_multi_downloadhandler(name):
    settings_mod = __import__(name, {}, {}, [''])
    settings_dict = settings_mod.__dict__
    # DOWNLOADER_MIDDLEWARES = getattr(settings_mod, 'DOWNLOADER_MIDDLEWARES')
    DOWNLOADER_MIDDLEWARES = settings_dict.setdefault('DOWNLOADER_MIDDLEWARES',{})
    DOWNLOADER_MIDDLEWARES['scrapy.contrib.downloadermiddleware.httpcompression.HttpCompressionMiddleware'] = None
    DOWNLOADER_MIDDLEWARES['scrapy.contrib.downloadermiddleware.chunked.ChunkedTransferMiddleware'] = None
    DOWNLOADER_MIDDLEWARES['feet8.core.middlewares.httpcompression.HttpCompressionMiddleware'] = 800
    DOWNLOADER_MIDDLEWARES['feet8.core.middlewares.chunked.ChunkedTransferMiddleware'] = 830
    DOWNLOADER_MIDDLEWARES['feet8.middlewares.multi.MultiMiddleware'] = 9000
    # DOWNLOAD_HANDLERS = getattr(settings_mod, 'DOWNLOAD_HANDLERS', None)
    DOWNLOAD_HANDLERS = settings_dict.setdefault('DOWNLOAD_HANDLERS', {})
    DOWNLOAD_HANDLERS['http'] = 'feet8.core.downloader.handlers.multi_dh.MultiDownloadHandler'
    DOWNLOAD_HANDLERS['https'] = 'feet8.core.downloader.handlers.multi_dh.MultiDownloadHandler'
