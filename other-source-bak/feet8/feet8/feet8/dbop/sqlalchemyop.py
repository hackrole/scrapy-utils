#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-5-15
"""
通过sqlalchemy提供关系数据库访问支持
当前使用sqlalchemy+sqlsoup.可支持sqlalchemy支持的所有类型数据库.
仅负责建立,关闭连接,使用orm或原始sql语句可自由选择.

note,若需要使用其他sqlalchemy的轻量级封装.像sqlsoup那样,封装db即可
若需要使用其他orm库,请在外单独实现.
"""
from __future__ import division, print_function, unicode_literals
from sqlalchemy import create_engine
from sqlsoup import SQLSoup
from feet8.dbop.utils import get_db_store_path, get_db_type_from_url

__metaclass__ = type

#mean sqlalchemy engine
db = None
db_type = ''
db_soup = None


def open_db(database, spider=None):
    #not complete-.-
    return False
    # global db, db_type, db_soup
    # open_db_kwargs = database['open_db_kwargs']
    # url = open_db_kwargs.pop('url')
    #
    # db_type = get_db_type_from_url(url)
    # if db_type == 'sqlite':
    #     path = get_db_store_path(settings, spider)
    #     db_url = db_url % {'path': path}
    # elif db_type == 'mysql':
    #     #todo add mysql support
    #     raise NotImplementedError('mysql is not supported yet')
    # db = create_engine(db_url, **db_kwargs)
    # db_soup = SQLSoup(db)
    # open_db_args = {'db_url': db_url}
    # open_db_args.update(db_kwargs)
    # return True, open_db_args


def close_db(spider=None):
    global db, db_soup
    db = None
    db_soup = None
