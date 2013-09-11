from selenium import WebDriver
from scrapy.http import Response
import os
from os.path import join, exists
from scrapy import signals
from scrapy.exceptions import NotConfigured, IgnoreRequest


class SeleniumParseMiddleare(object):
    def __init__(self):
        self.ff = WebDriver.Firefox()

    def process_request(request, spider):
        old_request = request
        print "<<<<<<<<<<<<<<<<<<<<<<<"
        print request.method
        if request.method = 'get':
            print "parse selenium"
            s = self.ff.get(request.url)
            test = self.ff.text

            return Response(text)

        return None

class RandomProxyMiddlerware(object):
    """random get a proxy from the PROXY_LIST, and set to the request"""

    def __init__(self, proxy_l):
        self.proxy_l = proxy_l

    @classmethod
    def from_crawler(cls, crawler):
        """init the crawler from the settings and make the proxy list"""
        if not crawler.settings.getbool("PROXYRANDOM_ENABLE"):
            raise NotConfigured
        proxy_file = crawler.settings.get("PROXYRANDOM_FILE")
        proxy_list = crawler.settings.getList("PROXYRANDOM_LIST")
        if proxy_file:
            proxy_l = cls._proxy_from_list()
        else if proxy_list:
            proxy_l = proxy_list
        else:
            print ">>>>>>>>>>>>>>configure error>>>>>>>>>>>>>>>>>>>>>"
            raise NotConfigured
        o = cls(proxy_l)

    @classmethod
    def _proxy_from_list(self, fp):
        """get the proxy list from file"""
        lines = open(fp).readlines()
        proxyes = [line.split('\t')[0].strip() for line in lines]
        return proxyes

    def process_request(self, request, spider):
        if 'proxy' in request.meta:
            return

        proxy = self.random_proxy()
        request.meta['proxy'] = proxy
