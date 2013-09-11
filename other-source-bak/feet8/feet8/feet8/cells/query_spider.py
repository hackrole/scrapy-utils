#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-13
"""
"""

from __future__ import division, print_function, unicode_literals


__metaclass__ = type

from bson.objectid import ObjectId

from scrapy import log

from feet8.cells.base_spider import Feet8BaseSpider
from feet8.utils import debug


class QuerySpider(Feet8BaseSpider):

    querys = []

    def __init__(self, *args, **kwargs):
        super(QuerySpider, self).__init__(*args, **kwargs)
        self.querys.extend(self.get_querys())

        #todo low move to another place
        if self.settings['DEBUG']:
            attrs_dic = debug.get_obj_attrs(self)
            log.msg(format='self.attrs:%(attrs_dic)s', attrs_dic=attrs_dic)

    def get_querys(self):
        return []

