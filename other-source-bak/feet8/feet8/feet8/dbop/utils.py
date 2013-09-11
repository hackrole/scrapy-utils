#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-6
"""
"""

from __future__ import division, print_function, unicode_literals
import inspect
import os
from urlparse import urlparse

__metaclass__ = type


def get_db_store_path(settings, spider=None):
    """
    判断数据库文件存储位置,用于sqlite与shelve
    store_path为目录时,存储在该目录加spider名字.data文件内
    store_path不是目录时,存储在该路径
    sotre_path为空时,若spider有,则在spider同目录
    否则在/tmp目录
    """
    database = settings.get('DATABASE', '')
    if not database:
        database = '.data'
    database_settings = settings.get('DATABASE_SETTINGS', {})
    store_path = database_settings.get('store_path', '')
    name = '%s.%s' % (getattr(spider, 'name', 'spider'), database)
    if os.path.isdir(store_path):
        path = os.path.join(store_path, name)
    else:
        path = store_path
    if not path:
        if spider is None:
            path = os.path.join('/tmp', name)
        else:
            path = inspect.getfile(spider.__class__)
            path = '%s.%s' % (path, database)
    return path


def get_db_type_from_url(url):
    """
    从数据库连接字符串中获得数据库类型
    例如:
    sqlite:/// -> sqlite.
    """
    dbs = [
        'sqlite',
        'mysql',
    ]
    url = url.lower()
    scheme = urlparse(url).scheme
    for db in dbs:
        if scheme.find(db) != -1:
            return db
    else:
        raise Exception('unknown db:%s' % url)