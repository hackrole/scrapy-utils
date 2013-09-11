#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-5-15
"""
shelve是一个本地kv数据库.
可用做快速开发,不过由于没有gui工具方便查看生成的数据.
推荐使用sqlalchemy,sqlite
"""
# deprected
# from __future__ import division, print_function, unicode_literals
#
# __metaclass__ = type
#
# import shelve
#
# from .utils import get_db_store_path
#
# db = None
#
#
# def open_db(settings, spider=None):
#     global db
#     path = get_db_store_path(settings, spider)
#     db = shelve.open(path)
#     open_db_args = {'db_url': path, }
#     return True, open_db_args
#
#
# def close_db(spider=None):
#     global db
#     db.close()


