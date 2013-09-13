#!/usr/bin/env python
# encoding: utf-8

from pymongo import connection
from scrapy import log
from scrapy import signals


class MongoSavePipeline(object):
    """
    save the item to the mongodb use pymongo.
    item's attr "_mongo_attrs"(dict) and mongo_save(method) is that maintains,
    the _mongo_attrs:
        not_save: if true, not save the item to mongodb
        collection: if set, use this collection for item save,else use the item class name's lower()

    the mongo_save:
        if set: use the item's mongo_save to save the item, else use global settings
    """

    def __init__(self, crawler):
        self.mongo_conf = crawler.settings.get('MONGODB_CONF', {})
        host = self.mongo_conf.get('HOST', 'localhost')
        port = self.mongo_conf.get('port', '27017')
        self.default_dbname = self.mongo_conf.get('db', 'item_scrapy')
        self.con = connection.Connection(host, port)
        self.db = self.con[self.default_dbname]

        # TODO: for index init and other things
        self.keys = settings.get('MONGODB_KEY', None)
        id_field = settings.get('MONGODB_ID_FIELD', '')
        safe = settings.get('MONGODB_SAFE', None)

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler)
        crawler.signals.connect(o.spider_close, signals.spider_closed)

        return o

    def spider_close(self, spider, reason):
        """ release the mongodb connection """
        self.con.close()

    def process_item(self, item, spider):
        """
        if item has mongo_save method, use it and return.
        else use the default save
        """
        if hasattr(item, 'mongo_save') and callable(item.mongo_save):
            item.mongo_save()
            return item
        else:
            self._save(item, spider)
            return item

    def _save(self, item, spider):
        """
        TODO: try finlly, benchmark, log debug/error
        """
        attrs = {}
        if hasattr(item, '_mongo_attrs'):
            attrs = item._mongo_attrs

        coll_name = self._mongo_attrs.get('collection_name', None)
        coll_name = item.__class__.lower() if not coll_name
        coll = self.db[coll_name]
        coll.insert(dict(item))


