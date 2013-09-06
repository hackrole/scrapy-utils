#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-3
"""

from __future__ import division, print_function, unicode_literals
from feet8.utils.digest import url_digest

__metaclass__ = type


class AttachmentMixin():

    def save_attachment(self, attach):
        # noinspection PyUnresolvedReferences
        db = self.db_mod.db
        collection = db['attachment_data']
        attach_url = attach.get('url', '')
        url_hash = attach.get('url_hash', '')
        if attach_url:
            attach['url_hash'] = url_digest(attach_url)
            if url_hash:
                attach['url_hash'] = url_hash
            spec = {'url_hash': attach['url_hash']}
            collection.update(spec, attach, upsert=True, w=0)
            return attach['url']
        else:
            doc_id = collection.insert(attach, w=0)
            return str(doc_id)

    def find_attachment(self, spec):
        # noinspection PyUnresolvedReferences
        db = self.db_mod.db
        return db['attachment_data'].find_one(spec)

    def find_attachment_by_url(self, url):
        # noinspection PyUnresolvedReferences
        db = self.db_mod.db
        spec = {'url_hash': url_digest(url)}
        return db['attachment_data'].find_one(spec)

    def find_attachment_by_id(self, _id):
        # noinspection PyUnresolvedReferences
        db = self.db_mod.db
        spec = {'_id': _id}
        return db['attachment_data'].find_one(spec)