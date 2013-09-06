#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-5-16
sogou_bbs爬虫
cmd:
scrapy crawl_ex sogou_bbs --logfile=/tmp/sogou_bbs.txt
"""
from __future__ import division, print_function, unicode_literals

__metaclass__ = type

import urllib

from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from feet8.cells.leg_spider import LegSpider
from feet8.spiders.bbs.utils import BbsMongodbAdapter, BbsItem
from feet8.utils.multi_convert import response_scrapy2mechanize, request_mechanize2scrapy
from feet8.utils.misc import response_html5parse, get_url_query, change_url_query


class SogouBbsSpider(LegSpider):
    name = 'sogou_bbs'

    querys = ['你好']

    entry_url = 'http://www.sogou.com/bbs/'
    search_form_order = 0
    search_input_name = 'query'
    next_page_word = '下一页>'
    visit_detail = True

    #spider kwargs
    intime = '一天内'  #一天内,一周内,一月内,一年内,全部时间
    page_count_limit = 0

    #db_adapter
    db_adapter_cls = BbsMongodbAdapter

    def get_query_request(self, response):
        intime = self.intime
        if intime == '全部时间':
            return super(SogouBbsSpider, self).get_query_request(response)
        # noinspection PyPropertyAccess
        br = self.br
        mechanize_response = response_scrapy2mechanize(response)
        br.set_response(mechanize_response)
        br.select_form(nr=self.search_form_order)
        query = response.meta['query']
        encoding = response.encoding
        query = query.encode(encoding)
        search_input_name = self.search_input_name.encode(encoding)
        br[search_input_name] = query
        br.submit()
        intime = intime.encode('utf8')
        query_request = br.click_link(text=intime)
        scrapy_request = request_mechanize2scrapy(query_request)
        scrapy_request.callback = self.query_callback
        url = scrapy_request.url
        query = get_url_query(url)
        query['num'] = 100
        new_url = change_url_query(url, query)
        new_request = scrapy_request.replace(url=new_url)
        return new_request

    def _ana_info_misc(self, hxs):
        site_name = ''
        pub_time = ''
        try:
            text = ''.join(hxs.extract())
            texts = text.split(' - ')
            site_name = texts[0]
            pub_time = texts[-1].split('\xa0-\xa0')[-1]
        finally:
            return site_name, pub_time

    def parse_list_page(self, response):
        multi_xpath = '//div[@class="results"]/div'
        html5_response = response_html5parse(response)
        hxs = HtmlXPathSelector(html5_response)
        multi_hxs = hxs.select(multi_xpath)
        for hxs in multi_hxs:
            title = ''.join(hxs.select('./h3//text()').extract())
            overview = ''.join(hxs.select('./div[@class="ft"]//text()').extract()
                               + hxs.select('./table[@class="vrbox"]//text()').extract())
            url = ''.join(hxs.select('./h3/a/@href').extract())
            url = urllib.unquote(url).strip()
            info_misc_hxs = hxs.select('.//cite//text()')
            site_name, pub_time = self._ana_info_misc(info_misc_hxs)
            doc = {
                'data_source': '搜狗论坛搜索',
                'site_name': site_name,
                'title': title,
                'pub_time': pub_time,
                'overview': overview,
                'url': url,
            }
            detail_url = url
            list_url = response.url
            query = response.meta.get('query')
            if not detail_url:
                next_request = None
            else:
                next_request = Request(detail_url, callback=self.parse_detail_page)
            item = BbsItem(doc=doc,
                           next_request=next_request, list_url=list_url, query=query)
            yield self.item_or_request(item)

    def parse_detail_page(self, response):
        item = response.meta['item']
        item['doc']['detail_pages'] = [response.body_as_unicode()]
        yield item

    def is_duplicate_request(self, request):
        if self._no_duplicate_request:
            return self.db_adapter.is_duplicate_request(request, BbsItem())
        else:
            return False