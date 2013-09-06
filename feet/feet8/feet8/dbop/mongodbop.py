#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-5-15
"""
"""
#未完成mongodb
from __future__ import division, print_function, unicode_literals
from feet8 import conf

__metaclass__ = type

import pymongo

db = None
conn = None

def open_db(database, spider=None):
    global db, conn
    open_db_kwargs = database['open_db_kwargs']
    url = open_db_kwargs.pop('url')
    db_name = database['db_name']
    conn = pymongo.Connection(url, **open_db_kwargs)
    db = conn[db_name]
    return True


def close_db(spider=None):
    global conn
    conn.close()



