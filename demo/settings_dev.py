#!/usr/bin/env python
#coding=utf8

from os import path
import time

# project dir path
PROJECT_DIR = path.dirname(path.dirname(path.realpath(__file__)))
# log file
cur_time_s = '_'.join([str(i) for i in time.localtime()[:4]])
log_file_name = ''.join(['run_', cur_time_s, '.log'])
LOG_FILE = path.join(PROJECT_DIR, 'logs',  log_file_name)

# Mysql conf
MySQL_HOST = "localhost"
MySQL_USER = "root"
MySQL_PASSWD = "root"

# mongo conf
MONGO_DB = "page"
MONGO_COLL = "things"

# item pipeline
# TODO:use for test mongo save
ITEM_PIPELINES = [
    #'lunwen.pipelines.MongoSavePipeline',
    'lunwen.pipelines.MongoSave2Pipeline',
    ]

# speed
CONCURRENT_ITEMS = 10
CONCURRENT_REQUESTS = 10
CONCURRENT_REQUESTS_PER_IP = 10
DOWNLOAD_DELAY = 5
RANDOMIZE_DOWNLOAD_DELAY = True

# 重定向
REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 5
REDIRECT_MAX_METAREFRESH_DELAY = 100

# download timeout and retry
DOWNLOAD_TIMEOUT = 30
DOWNLOAD_DEBUG = True
DOWNLOAD_STATS = True
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 503, 504, 400, 408]

# http cache
#HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SESC = 0 # never lost the cache
HTTPCACHE_DIR = path.join(PROJECT_DIR, 'caches/')
HTTPCACHE_IGNORE_HTTP_CODES = [404, 500]
