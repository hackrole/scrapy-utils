#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-11
"""



#
CLOSESPIDER_PAGECOUNT = 0
CLOSESPIDER_ITEMCOUNT = 0
# LOG_LEVEL = 'INFO'

#mongodb test
DATABASE = {
    'dbop': 'mongodb',
    'open_db_kwargs': {
        'url': 'mongodb://192.168.56.101:37017',
    },
    'db_name': 'feet8',
}
#mongodb online
# DATABASE = {
#     'dbop': 'mongodb',
#     'open_db_kwargs': {
#         'url': 'mongodb://mygod:damn@112.11.119.236:37017',
#     },
#     'db_name': 'feet8',
# }



SPIDER_MIDDLEWARES = {
    # 'feet8.middlewares.item.ItemErrorSaveSpiderMiddleware': 30,
    'feet8.middlewares.dupfilter.DupfilterMiddleware': 1100,
}

DOWNLOADER_MIDDLEWARES = {
    'feet8.middlewares.more_browser.MoreBrowserMiddleware': 1000,
    'feet8.middlewares.priority.PriorityMiddleware': 1200,
    'feet8.middlewares.item.ItemErrorSaveDownloaderMiddleware': 30,
}

ITEM_PIPELINES = [
    'feet8.pipelines.attachment.AttachmentPipeLine',
    'feet8.pipelines.save_item.SaveItemPipeline',
]


#
# PROXY_MODE = 'block'
# PROXY_INTERVAL = 10