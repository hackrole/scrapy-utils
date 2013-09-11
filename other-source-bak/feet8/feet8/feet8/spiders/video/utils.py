#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-7-1
"""
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type


import datetime
from itertools import chain

from scrapy.item import Field

from feet8.utils.digest import url_digest
from feet8.items.doc_item import DocItem
from feet8.dbop.leg_db_adapter import LegDbAdapter


class VideoItem(DocItem):
    collection = Field(default='video_data')
    item_doc_length = None

    def process_item(self, spider):
        now = datetime.datetime.utcnow()
        doc = self['doc']
        doc.pop('detail_url', None)
        #计算部分
        site_url_hash = url_digest(doc['url'])
        calc_doc = {
            'url_hash': site_url_hash,
        }
        default_doc1 = {
            'spider_name': spider.name,
            'data_type': '视频',
            'crawl_time': now,
            'query': self['query'],
        }
        all_doc = chain(calc_doc.iteritems(), default_doc1.iteritems())
        for k, v in all_doc:
            doc.setdefault(k, v)
        doc['attachments'] = self['attachments']


class VideoMongodbAdapter(LegDbAdapter):

    correct_dbop_type = 'mongodb'

