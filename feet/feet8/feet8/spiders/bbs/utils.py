#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-26
"""
"""

from __future__ import division, print_function, unicode_literals
from scrapy.item import Field
from feet8.dbop.db_adapter import DbAdapter
from feet8.utils.algorithm import get_content
from feet8.utils.misc import is_duplicate_request_by_url

__metaclass__ = type


import datetime
from itertools import chain

from feet8.utils.digest import url_digest
from feet8.items.doc_item import DocItem

# noinspection PyUnresolvedReferences
from boilerpipe.extract import Extractor


class BbsItem(DocItem):
    collection = Field(default='bbs_data')
    item_doc_length = None

    def process_item(self, spider):
        now = datetime.datetime.utcnow()
        doc = self['doc']
        doc.pop('detail_url', None)
        #计算部分
        site_url_hash = url_digest(doc['url'])
        content = ''.join([get_content(page) for page in doc.get('detail_pages', [])])
        calc_doc = {
            'url_hash': site_url_hash,
            'content': content,
        }
        #提取数据的默认填充部分
        default_doc1 = {
            'spider_name': spider.name,
            'data_type': '论坛',
            'crawl_time': now,
            'query': self['query'],
        }
        all_doc = chain(calc_doc.iteritems(), default_doc1.iteritems())
        for k, v in all_doc:
            doc.setdefault(k, v)


class BbsMongodbAdapter(DbAdapter):

    correct_dbop_type = 'mongodb'

    def save_item(self, item):
        db = self.db_mod.db
        collection = item['collection']
        doc = item['doc']
        spec = {'url_hash': doc['url_hash']}
        db[collection].update(spec, doc, upsert=True, w=0)

    def is_duplicate_request(self, request, item):
        return is_duplicate_request_by_url(self, request, item)



