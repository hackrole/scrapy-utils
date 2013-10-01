#!/usr/bin/env python
# encoding: utf-8

import gevent
from gevent import monkey

monkey.patchall()

from gevent import queue
from gevent import pool
import requests


class Request(object):
    """
    the request object for queue
    TODO: not finish.
    """
    def __init__(self, url, method="GET", headers={}, cookie=None,
                 body=None):
        self.url = url
        self.method = method
        self.headers = headers
        self.cookie = cookie
        self.body = body


class BaseSpider(object):
    """
    the base object for spider
    """
    def __init__(self, download_pool=10):
        self.request_queue = queue.Queue()
        self.download_pool = pool.Pool(download_pool)
        self.response_queue = queue.Queue()

    def start_requests(sel):
        for url in self.start_urls:
            req = Request(url)
            self.request_queue.put(req)
        self.start()

    def run(self):
        self.start_requests()

    def start(self):
        assert not self.request_queue.empty(), "request queue is empty now"
        count = self.request_queue.qsize()
        self.download_pool.map(self._download, xrange(count))
        self.download_pool.join()

        response_count = self.response_count.qsize()
        self.parse_pool.map(self._parse, xrange(count))
        self.parse_pool.join()

        self.start()

    def _download(self):
        request = self.request_queue.get(timeout=10)
        response = requests.get(request.url)
        if response.status == 200:
            self.response_queue.put(response)

    def _parse(self):
        response = self.response_queue.get(timeout=10)
        reqs = self.parse(response.text)
        for req in reqs:
            self.request_queue.put(req)

