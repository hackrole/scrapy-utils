#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-9
"""

from __future__ import division, print_function, unicode_literals
import youku_lixian.common

__metaclass__ = type

urls_container = {}


#def download_urls(urls, title, ext, total_size, output_dir='.', refer=None, merge=True):

def _download_urls(urls, title, ext, total_size, output_dir='.', refer=None, merge=True, **kwargs):
    urls_container = kwargs.pop('container', [])
    urls_container = urls
    return

youku_lixian.common.download_urls = _download_urls


def parse_video_urls(url):
    urls_container = []


