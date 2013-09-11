#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-11
"""



#
CLOSESPIDER_PAGECOUNT = 0
CLOSESPIDER_ITEMCOUNT = 0
LOG_LEVEL = 'INFO'

# mongodb online
DATABASE = {
    'dbop': 'mongodb',
    'open_db_kwargs': {
        'url': 'mongodb://mygod:damn@112.11.119.236:37017',
    },
    'db_name': 'feet8',
}


SPIDER_MIDDLEWARES = {
    # 'feet8.middlewares.item.ItemErrorSaveSpiderMiddleware': 30,
    # 'feet8.middlewares.dupfilter.DupfilterMiddleware': 1100,
}

DOWNLOADER_MIDDLEWARES = {
    'feet8.middlewares.priority.PriorityMiddleware': 1200,
    # 'feet8.middlewares.item.ItemErrorSaveDownloaderMiddleware': 30,
}



PROXY_MODE = 'block'
PROXY_INTERVAL = 10

RETRY_TIMES = 4