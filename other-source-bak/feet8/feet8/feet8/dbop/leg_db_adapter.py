#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-2
"""

from __future__ import division, print_function, unicode_literals
from feet8.dbop.attachment_mixin import AttachmentMixin
from feet8.dbop.db_adapter import DbAdapter
from feet8.utils.digest import url_digest

__metaclass__ = type


class LegDbAdapter(DbAdapter, AttachmentMixin):
    _save_item_type = 'cover'   #'cover'|'set'

    def save_item(self, item, spider=None):
        db = self.db_mod.db
        collection = item['collection']
        doc = item['doc']
        spec = {'url_hash': doc['url_hash']}
        if self._save_item_type == 'cover':
            db[collection].update(spec, doc, upsert=True, w=0)
        elif self._save_item_type == 'set':
            db[collection].update(spec, {'$set': doc}, upsert=True, w=0)

    def is_duplicate_request(self, request, item):
        db = self.db_mod.db
        collection = item['collection']
        url_hash = url_digest(request.url)
        spec = {'url_hash': url_hash}
        doc = db[collection].find_one(spec)
        if doc:
            return True
        else:
            return False
