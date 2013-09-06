#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-5-30
"""
这是对sep19需要实现功能的一个简便实现
无需修改scrapy
"""

from __future__ import division, print_function, unicode_literals
from scrapy.utils.misc import load_object

__metaclass__ = type
from scrapy.commands import crawl


class Command(crawl.Command):
    """
    优先级为
    1,命令行settings
    2,spider settings
    3,settings
    4,default settings
    """

    requires_project = True

    def syntax(self):
        return "[options] <spider>"

    def short_desc(self):
        return "Start crawling from a spider or URL"

    def process_options(self, args, opts):
        self.process_spider_settings(args)
        super(Command, self).process_options(args, opts)

    def process_spider_settings(self, args):
        spman_cls = load_object(self.settings['SPIDER_MANAGER_CLASS'])
        spman_obj = spman_cls.from_settings(self.settings)
        spname = args[0]
        spcls = spman_obj._spiders[spname]
        self.settings.overrides.update(spcls._custom_settings())
