#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-7
"""
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type

import copy
import json
from bson import ObjectId

from scrapy.spider import BaseSpider
import feet8.settings


class Feet8BaseSpider(BaseSpider):
    """
    功能:
    1,sep19的hack实现,每spider一个settings
    """

    custom_settings = {}
    spider_kwargs = {}
    spider_run_id = None


    def __init__(self, *args, **kwargs):
        super(Feet8BaseSpider, self).__init__(*args, **kwargs)
        # noinspection PyUnresolvedReferences
        self.spider_kwargs = json.loads(kwargs.get('spider_kwargs', '{}'))
        for k, v in self.spider_kwargs.iteritems():
            setattr(self, k, v)
        #spider运行id
        # noinspection PyUnresolvedReferences
        self.spider_run_id = str(ObjectId())

    @property
    def settings(self):
        if getattr(self, '_crawler', None):
            return super(Feet8BaseSpider, self).settings
        else:
            global_settings = feet8.settings
            this_settings = copy.copy(global_settings.__dict__)
            custom_settings = self.__class__._custom_settings()
            this_settings.update(custom_settings)
            return this_settings

    @classmethod
    def _custom_settings(cls):
        """
        这是对sep19的一个hack实现,不需要修改scrapy
        通过定制命令scrapy crawl_ex实现.详见feet8.commands.crawl_ex
        在这里的优先级为
        spiderclass.custom_settings 覆盖 spidername_settings.py的设置
        """
        custom_settings = {}
        _custom_settings_path = '%s_settings' % cls.__module__
        try:
            mod = __import__(_custom_settings_path, {}, {}, [''])
            custom_settings.update(mod.__dict__)
            # test
            # if _settings.get('IMPORT_SPIDER_GLOBAL_SETTINGS', True):
            #     _path = 'settings'
            #     try:
            #         mod = __import__(_path, {}, {}, [''])
            #         _settings.update(mod.__dict__)
            #     except ImportError:
            #         pass
            # test end
        except ImportError:
            pass
        cls_custom_settings = getattr(cls, 'custom_settings', {})
        custom_settings.update(cls_custom_settings)
        return custom_settings

    #如果太多就整合成一个mixin
