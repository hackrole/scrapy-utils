#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-16
"""

from __future__ import division, print_function, unicode_literals
from urlparse2 import urlparse
from feet8.utils.multi_convert import headers_scrapy2dict

__metaclass__ = type

import time

from scrapy.utils.decorator import inthread
from scrapy.responsetypes import responsetypes
from scrapy.http.headers import Headers
import requests


class RequestsDownloadHandler(object):
    """
    暂未完全支持所有功能,如验证.
    勉强支持代理-.-
    """
    _session = None
    timeout = 180

    def __init__(self, settings):
        self.single_session = settings.get('REQUESTS_SINGLE_SESSION', False)
        self.proxies = settings.get('PROXIES', [])
        if self.single_session:
            self._session = requests.sessions.Session()

    def download_request(self, request, spider):
        download = self._download_request
        defer = download(request, spider)
        return defer

    @inthread
    def _download_request(self, request, spider):
        proxies = {}
        proxy = request.meta.get('proxy', '')
        if proxy:
            for p in self.proxies:
                if p.find(proxy) != -1:
                    scheme = urlparse(p).scheme
                    proxies[scheme] = p
                    break
        timeout = request.meta.get('download_timeout', self.timeout)
        url = request.url
        method = request.method
        headers = headers_scrapy2dict(request.headers)
        data = request.body
        session = self._session or requests.sessions.Session()
        st = time.time()
        requests_response = session.request(method, url, headers=headers, data=data, timeout=timeout, proxies=proxies)
        et = time.time()
        cost = et - st
        request.meta['download_latency'] = cost
        headers = Headers(dict(requests_response.headers))
        respcls = responsetypes.from_args(headers=headers,
                                          url=requests_response.url,
                                          body=requests_response.content)
        response_url = requests_response.url.encode(requests_response.encoding)
        response = respcls(url=response_url,
                           status=requests_response.status_code,
                           headers=headers,
                           body=requests_response.content, )
        return response

