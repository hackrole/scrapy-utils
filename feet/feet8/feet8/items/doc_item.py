#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-7
"""

"""

from __future__ import division, print_function, unicode_literals
import os
from scrapy.item import Field
from feet8.items.base_item import Feet8BaseItem
from feet8.items.item_common_mixin import ItemCommonMixin

__metaclass__ = type



class DocItem(Feet8BaseItem, ItemCommonMixin, ):
    #谨慎使用这里的default,发现靠不住,感觉多个item间的修改可能被共享-.-
    collection = Field(default='')
    doc = Field(default={})
    query = Field(default='')
    next_request = Field(default=None)
    list_url = Field(default='')
    attachments = Field(default=[])
    attachment_urls = Field(default=[])

    item_doc_length = None

    def validate_item(self, spider):
        doc = self['doc']
        msg = 'item[\'doc\'] validate ok'
        if not self.item_doc_length:
            return True, msg
        item_doc_length = len(doc.keys())
        if item_doc_length == self.item_doc_length:
            return True, msg
        else:
            msg = 'item[\'doc\'] lack fields,need:%d,current:%d' % (self.item_doc_length, item_doc_length)
            return False, msg

