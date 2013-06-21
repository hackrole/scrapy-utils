#!/usr/bin/env python
#coding=utf8

import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

# set the config for read db conf
# TODO: set to the settings file
config_file = "/var/www/lunwen/lunwen/utils/db.conf"
config = ConfigParser.ConfigParser()
config.read(config_file)
# read the db conf
db_driven = 'mysql'
db_host = config.get(db_driven, 'host')
db_user = config.get(db_driven, 'user')
db_passwd = config.get(db_driven, 'passwd')
db_database = config.get(db_driven, 'db')
db_charset = config.get(db_driven, 'charset')

# get the db connect engine for use
mysql_url = URL(db_driven, username=db_user, password=db_passwd, host=db_host,
        database=db_database, query={'charset':db_charset,})
engine = create_engine(mysql_url, echo=False)

def get_keywords():
    sql = "select id, keyword from keyword"
    result = engine.execute(sql)
    return result
