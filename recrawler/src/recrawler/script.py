#!/usr/bin/env python
#coding=utf-8

import config
import PySQLPool
from htmlcontent import Extractor
import redis

POOL = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)

connection = PySQLPool.getNewConnection(
    username=config.DB_USER,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
    db=config.DB_DB,
    charset=config.DB_CHARSET)

ext = Extractor()


def sync_content(urlhash):

    query = PySQLPool.getNewQuery(connection)
    print urlhash
    query.Query('''select html from news_html where url_hash=%s;''',
               (urlhash,))
    if query.record:
        html = query.record[0]['html']
        ext_content = ext.get_content(html, True, with_tag=False)
        if ext_content != '':
            query.Query('update data_news2 set content=%s where url_hash=%s;',
                       (ext_content, urlhash))
            query.Pool.Commit()
    return True

if __name__ == '__main__':
    c = open('empty_urlhash', 'r').readlines()
    urlhashes = [line.strip() for line in c]
    map(sync_content, urlhashes)
