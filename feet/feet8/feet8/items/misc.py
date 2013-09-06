#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-4
"""

from __future__ import division, print_function, unicode_literals
from bson import ObjectId
from feet8.utils.algorithm import get_content

__metaclass__ = type

def calc_item_content(doc, spider):
    pages = []
    for attach_id in doc['attachments']:
        if isinstance(attach_id, ObjectId):
            attach = spider.db_adapter.find_attachment_by_id(attach_id)
        else:
            attach = spider.db_adapter.find_attachment_by_url(attach_id)
        if attach:
            mime_type = attach.get('mime_type', '')
            if mime_type == 'text/html':
                pages.append(attach.get('data', ''))
    content = ''.join([get_content(page) for page in pages])
    return content