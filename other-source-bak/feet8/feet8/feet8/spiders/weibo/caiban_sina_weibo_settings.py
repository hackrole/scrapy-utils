#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-3
"""
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type

# #mongodb test
# DATABASE = {
#     'dbop': 'mongodb',
#     'open_db_kwargs': {
#         'url': 'mongodb://192.168.56.101:37017',
#     },
#     'db_name': 'feet8',
# }

#mongodb online
DATABASE = {
    'dbop': 'mongodb',
    'open_db_kwargs': {
        'url': 'mongodb://mygod:damn@112.11.119.236:37017',
    },
    'db_name': 'feet8',
}

DOWNLOAD_TIMEOUT = 30   #访问超时
CONCURRENT_REQUESTS = 1024   #全局并发请求
CONCURRENT_REQUESTS_PER_IP = 0
CONCURRENT_REQUESTS_PER_DOMAIN = 4  #每域名并发请求数
DOWNLOAD_DELAY = 10  #请求延迟
AUTOTHROTTLE_ENABLED = True #自动调整请求频率- -.

#
CLOSESPIDER_PAGECOUNT = 0
CLOSESPIDER_ITEMCOUNT = 0
LOG_LEVEL = 'INFO'


SPIDER_MIDDLEWARES = {
    'feet8.middlewares.item.ItemErrorSaveSpiderMiddleware': 30,
}


DOWNLOADER_MIDDLEWARES = {
    'feet8.middlewares.more_browser.MoreBrowserMiddleware': 1000,
    'feet8.spiders.weibo.utils.CaibanSinaWeiboMiddleware': 650,
    'feet8.middlewares.item.ItemErrorSaveDownloaderMiddleware': 30,
}

#_login
USERS = [
    # ('tpcrawler_1@sina.com', 'let5in'),
    # ('yardz01@sina.com', '88!@info'),
    # ('seuzer49@163.com', '88!@info'),
    # ('18369480971', '480971'),   #白
    ('18369572372', 'oquwgtiu8126x'),    #初级
    ('15978335625', 'liogai2206m'),  #高级
    # ('18273159543', 'kgllxhm645025z'),   #达人
]
GSID_MAX_TIMES = 10000



