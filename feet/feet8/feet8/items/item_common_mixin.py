#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-7
"""
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type


class ItemCommonMixin():
    """
    提供spider与item相关的交互.另见cells.SpiderItemMixin
    包括预处理(用来填写默认值,计算hash等)
    item校验(数据合规性校验)
    数据库读写
    """

    def before_process_item(self, spider):
        pass

    def process_item(self, spider):
        raise NotImplementedError

    def after_process_item(self, spider):
        pass

    def validate_item(self, spider):
        raise NotImplementedError

