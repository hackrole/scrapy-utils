#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-19
"""
"""

from __future__ import division, print_function, unicode_literals
from feet8.middlewares.dupfilter import DupRequestError
from scrapy import log

__metaclass__ = type
#
# class SilenceMiddleware(object):
#
#
#     def process_spider_input(self, response, spider):
#         if 200 <= response.status < 300: # common case
#             return
#         meta = response.meta
#         if 'handle_httpstatus_all' in meta:
#             return
#         if 'handle_httpstatus_list' in meta:
#             allowed_statuses = meta['handle_httpstatus_list']
#         else:
#             allowed_statuses = getattr(spider, 'handle_httpstatus_list', ())
#         if response.status in allowed_statuses:
#             return
#         raise HttpError(response, 'Ignoring non-200 response')
#
#     def process_spider_exception(self, response, exception, spider):
#         if isinstance(exception, DupRequestError):
#             log.msg(format='DupFilterMiddleware,dup request:%(request)s', request=exception.request,spider=spider)
#             return []