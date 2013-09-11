#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-1
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type


class SaveItemPipeline(object):

    def process_item(self, item, spider):
        spider._save_item(item)
        return item