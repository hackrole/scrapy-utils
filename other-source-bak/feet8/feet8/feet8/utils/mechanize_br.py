#coding=utf8
#!/usr/bin/env python
from __future__ import division, print_function, unicode_literals

__metaclass__ = type

#Author:wuya @ smallteam
#Date: 13-5-13

import cookielib
import mechanize
from mechanize import Browser, RobustFactory
from mechanize._http import HTTPRefreshProcessor
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36'


def set_timeout(timeout):
    import mechanize._sockettimeout
    mechanize._sockettimeout._GLOBAL_DEFAULT_TIMEOUT = timeout
set_timeout(30)


def back_func():
    raise Exception('this mechanize conf to no history')


class NoHistory(object):
    def add(self, *a, **k): pass
    def clear(self): pass
    def close(self): pass


def get_br():
    #todo low
    #headers
    #Accept-Encoding: identity
    # Host: _login.weibo.cn
    # Referer: http://weibo.cn/
    # Connection: close
    # User-Agent: Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)
    br = Browser(factory=RobustFactory(), history=NoHistory(),)
    cj = cookielib.LWPCookieJar()
    br.back = back_func
    br.set_cookiejar(cj)
    br.set_handle_equiv(True)
    #br.set_handle_gzip(True) #gzip在mechanize里面还不是正式功能
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(HTTPRefreshProcessor(), max_time=10)
    br.addheaders = [('User-agent', USER_AGENT)]
    return br