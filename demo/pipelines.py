# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

import pymongo
from scrapy import log


class MongoSavePipeline(object):
    """save the item to mongo db"""

    def process_item(self, item, spider):
        if hasattr(item, 'mongo_save') and callable(item.mongo_save):
            item.mongo_save()
            print "mongo save"

        return item

class SqlSave2Pipeline(object):
    """ save the item to mysql db """

    def __init__(self, db, host="localhost", user="root",
            passwd="root", charset="utf8", db_driven="mysql"):
        self.db = db
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db_driven = db_driven
        mysql_url = URL(db_driven, username=user, password=passwd,
                host=host, database=db, query={'charset':charset,})
        engine = create_engine(mysql_url, echo=True)
        self.engine = engine

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        host = settings.get('DB_HOST', 'localhost')
        user = settings.get('DB_USER', 'root')
        passwd = settings.get('DB_PASSWD', 'root')
        db = settings.get('DB_DB', 'ssc')
        charset = settings.get('DB_CHAR', 'utf8')
        db_driven = settings.get('DB_DRIVEN', 'mysql')
        return cls(db, host, user, passwd, charset, db_driven)

    def process_item(self, item, spider):
        key = ','.join(item.keys())
        value = item.values()
        s = ",".join(['%s' for i in value])
        tb_name = item.tablename()
        sql = "insert into %s (%s) values (%s)" % (tb_name, key, s)
        self.engine.execute(sql, value)
        print "sql save"

class MongoSave2Pipeline(object):
    """save the item to mongo db, use extension"""

    def __init__(self, db, collection, host='localhost', port=None, keys=None, id_field=None, safe=None):
        con = pymongo.connection.Connection(host, port)
        self.db = con[db]
        self.collection = self.db[collection]
        self.keys = keys
        self.id_field = id_field
        self.safe = safe

        if isinstance(self.keys, basestring) and self.keys == "":
            self.keys = None

        if self.keys:
            self.collection.ensure_index(self.keys, unique=True)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        host = settings.get('MONGODB_HOST', 'localhost')
        port = settings.get('MONGODB_PORT', 27017)
        db = settings.get('MONGODB_DB', 'scrapy')
        collection = settings.get('MONGODB_COLLECTION', 'wanfang')
        keys = settings.get('MONGODB_KEY', None)
        id_field = settings.get('MONGODB_ID_FIELD', '')
        safe = settings.get('MONGODB_SAFE', None)
        return cls(db, collection, host, port, keys, id_field, safe)

    def process_item(self, item, spider):
        result = self.collection.insert(dict(item), safe=self.safe)
        msg = 'Item %s wrote to mongodb %s/%s' % (result, self.db, self.collection)
        #log.msg(msg, level=log.DEBUG, spider=spider)
        return item


