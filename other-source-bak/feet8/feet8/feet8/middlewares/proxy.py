#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-10
"""

from __future__ import division, print_function, unicode_literals
import random
import re
from scrapy import log
from scrapy.exceptions import NotConfigured
import time

__metaclass__ = type

import base64
from urllib import unquote, proxy_bypass
from urllib2 import _parse_proxy
from urlparse import urlunparse

from scrapy.utils.httpobj import urlparse_cached


class Proxy:
    def __init__(self, url):
        self.url = url
        proxy_type, user, password, hostport = _parse_proxy(url)
        proxy_url = urlunparse((proxy_type or 'http', hostport, '', '', '', ''))
        if user and password:
            user_pass = b'%s:%s' % (unquote(user), unquote(password))
            creds = base64.b64encode(user_pass).strip()
        else:
            creds = None
        self.proxy_type = proxy_type
        self.user = user
        self.password = password
        split_result = hostport.split(':')
        self.host = split_result[1]
        if len(split_result) == 2:
            self.port = split_result[-1]
        self.proxy_url = proxy_url
        self.creds = creds
        self.last_use_time = 0
        self.last_success_time = 0
        self.last_fail_time = 0
        self.use_count = 0
        self.success_count = 0
        self.fail_count = 0

    def choice(self):
        log.msg('ProxyMiddleware:use proxy %s' % self.proxy_url, log.DEBUG)
        now = time.time()
        self.last_use_time = now
        self.use_count += 1

    def success(self):
        log.msg('ProxyMiddleware:use proxy %s success' % self.proxy_url, log.DEBUG)
        now = time.time()
        self.last_success_time = now
        self.success_count += 1

    def fail(self):
        log.msg('ProxyMiddleware:use proxy %s fail' % self.proxy_url, log.DEBUG)
        now = time.time()
        self.last_fail_time = now
        self.fail_count += 1


class ProxyMiddleware(object):
    def __init__(self, crawler):
        settings = crawler.settings
        self._proxies = settings.get('PROXIES')
        if not self._proxies:
            raise NotConfigured
        self.max_retry_times = settings.getint('RETRY_TIMES')
        self.no_proxy_urls = settings.get('NO_PROXY_URLS', [])
        self.no_proxy_patterns = [re.compile(regex) for regex in self.no_proxy_urls]
        self.proxy_mode = settings.get('PROXY_MODE', 'nonblock')    #block|nonblock|random
        self.proxy_interval = settings.get('PROXY_INTERVAL', 0)
        self.local_interval = settings.get('PROXY_LOCAL_INTERVAL', self.proxy_interval)
        self.proxies = [Proxy(url) for url in self._proxies]
        self._last_choiced_proxy_index = -1
        self.local_last_use_time = 0

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        for p in self.no_proxy_patterns:
            if p.search(request.url):
                return
        retries = request.meta.get('retry_times', None)
        #已手动制定代理的不设置
        if 'proxy' in request.meta:
            if retries is None:
                return

        #当到达最大重试次数时，使用本机直接访问，确保失败时始终有一次本机访问.
        if retries == self.max_retry_times:
            now = time.time()
            should_sleep = self.local_interval - (now - self.local_last_use_time)
            if should_sleep > 0:
                log.msg('ProxyMiddleware:use proxy fail,local sleep %s' % should_sleep, log.DEBUG)
                time.sleep(should_sleep)
            return

        parsed = urlparse_cached(request)
        scheme = parsed.scheme
        # 'no_proxy' is only supported by http schemes
        if scheme in ('http', 'https') and proxy_bypass(parsed.hostname):
            return
        self._set_proxy(request, scheme)

    def _set_proxy(self, request, scheme):
        """
        目前只支持basic的验证,支持其他验证方式再议.
        """
        if scheme not in ['http']:
            return
        proxy = self.choice_proxy()
        request.meta['proxy'] = proxy.proxy_url
        creds = proxy.creds
        if creds:
            request.headers['Proxy-Authorization'] = 'Basic ' + creds

    def choice_proxy(self):
        now = time.time()
        if self.proxy_mode == 'nonblock':
            self._last_choiced_proxy_index += 1
            self._last_choiced_proxy_index %= len(self.proxies)
            proxy = self.proxies[self._last_choiced_proxy_index]
            proxy.choice()
            return proxy
        elif self.proxy_mode == 'block':
            while True:
                times = [proxy.last_use_time for proxy in self.proxies]
                min_time = min(times)
                if now - min_time < self.proxy_interval:
                    # log.msg('ProxyMiddleware:no proxy fit,sleep 0.1', log.DEBUG)
                    time.sleep(0.1)
                    now = time.time()
                    continue
                else:
                    for index, proxy in enumerate(self.proxies):
                        if proxy.last_use_time == min_time:
                            self._last_choiced_proxy_index = index
                            proxy.choice()
                            return proxy
        else:
            proxy = random.choice(self.proxies)
            for index, _proxy in enumerate(self.proxies):
                if proxy == _proxy:
                    self._last_choiced_proxy_index = index
                    proxy.choice()
                    return proxy
