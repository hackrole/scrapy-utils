#!/usr/bin/env python
#coding=utf8

from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.shell import inspect_response
from scrapy.utils.response import open_in_browser
from scrapy.selector import HtmlXPathSelector

# the urls to be use
SEARCH_URL = ''
SEARCH_BASE = ''

class DemoSpider(BaseSpider):
    name = ''
    allowed_domains = []
    start_urls = []

    def start_requests(self):
        """use the keyword to make the search and parse request"""
        self.crawler.stats.set_value('search_time', 0)
        self.crawler.stats.set_value('list_time', 0)
        self.crawler.stats.set_value('detail_time', 0)
        self.crawler.stats.set_value('error_time', 0)

        self.crawler.stats.inc_value('search_time')

        # the request proxy get and set
        proxy = common.random_proxy()
        meta ={'kw': word, 'proxy':proxy}

        # yield request
        yield Request(search_url, meta=meta,
                callback=self.parse_list,
                errback=self.parse_error
                dont_filter=True)
        # make request
        #self.make_request_from_url(url, callback=self.parse_list,
                #errback=self.parse_error)

    def parse_error(self, failure):
        self.crawler.stats.inc_value('error_time')
        failure.printTraceback()

        self.log('msg', loglevel=Error)
        r = failure.request
        msg = '\r'.join([str(r.url), r.body])
        self.log(msg)

    def parse_list(self, reponse):
        # the selector build and the data meta
        hxs = HtmlXPathSelector(response)
        meta = response.meta
        # log msg
        self.log('msg', loglevel=Error)

        # for debug and first xpath write
        open_in_browser(response)
        inspect_response(response, self)

        # selector choose and join or strip
        ''.join(hxs.select('').extract()).strip()

        # url join
        base_url = get_base_url(response)
        n_url = urljoin_rfc(base_url, 'url')

        return item
