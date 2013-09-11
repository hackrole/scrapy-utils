#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-3
"""
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type

from feet8.utils.settings import import_spider_global_settings, use_multi_downloadhandler

import_spider_global_settings(__package__, __name__)

DOWNLOAD_TIMEOUT = 30   #访问超时
CONCURRENT_REQUESTS = 1024   #全局并发请求
CONCURRENT_REQUESTS_PER_IP = 0
#有频率限制,太快会弹验证码
CONCURRENT_REQUESTS_PER_DOMAIN = 1  #每域名并发请求数
DOWNLOAD_DELAY = 1  #请求延迟
AUTOTHROTTLE_ENABLED = True #自动调整请求频率- -.

# DOWNLOADER_MIDDLEWARES['feet8.middlewares.proxy.ProxyMiddleware'] = 1100
DOWNLOADER_MIDDLEWARES['feet8.middlewares.immediate_response.ImmediateResponseMiddleware'] = 1500
# REDIRECT_ENABLED = False

# use_multi_downloadhandler(__name__)
# DEFAULT_DOWNLOAD_HANDLER = 'requests'
# REQUESTS_SINGLE_SESSION = False
#
# NO_PROXY_URLS = [
#     # 'http://books.daweisoft.com\S*'
# ]
COOKIES_ENABLED = True