#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-6
"""
scrapy的数据库相关模块
"""
from __future__ import division, print_function, unicode_literals
from scrapy import signals, log


__metaclass__ = type


class DbManager():
    """
    现在支持mongodb, mysql, shelve, sqlite
    mongodb:
    mysql:
    shelve:
    sqlite:
    """
    _db_mod = None

    def __init__(self, settings):
        self.settings = settings
        database = settings['DATABASE']
        dbop = database['dbop'].lower()
        self.dbop = dbop
        mod_path = 'feet8.dbop.%sop' % dbop
        mod = __import__(mod_path, {}, {}, [''])
        self.db_mod = mod

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        ext = cls(settings)
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext

    def spider_opened(self, spider):
        try:
            spider.db_adapter = spider.db_adapter_cls(self.db_mod, self.dbop)
            database = self.settings['DATABASE']
            result = self.db_mod.open_db(database, spider)
        except Exception as e:
            log.msg(format='DbManager:error %(error)s', level=log.ERROR, error=e)
            result = False
        if result:
            log.msg(format='DbManager:use %(database)s', level=log.INFO, database=self.dbop)
            log.msg(format='DbManager:connect database success', level=log.INFO)
        else:
            log.msg(format='DbManager:connect database fail', level=log.ERROR)
            raise Exception('DbManager:open_db fail')

    def spider_closed(self, spider):
        self.db_mod.close_db(spider)
        log.msg(format="DbManager:database connection closed", level=log.INFO)


