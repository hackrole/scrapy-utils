#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-5-13
"""
qihoo_bbs爬虫
cmd:
scrapy crawl_ex qihoo_bbs --logfile=/tmp/qihoo.txt
"""
from __future__ import division, print_function, unicode_literals

__metaclass__ = type

import re
import urllib

from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from feet8.cells.leg_spider import LegSpider
from feet8.utils.misc import response_html5parse,try_int_or_0, get_url_query, change_url_query
from feet8.spiders.bbs.utils import BbsItem, BbsMongodbAdapter
from feet8.utils.multi_convert import response_scrapy2mechanize, request_mechanize2scrapy

class QihooBbsSpider(LegSpider):
    name = 'qihoo_bbs'

    querys = ['今天']

    entry_url = 'http://www.qihoo.com/bbs/index.html?kw='
    search_form_order = 0
    search_input_name = 'kw'
    next_page_word = '下一页'
    visit_detail = True

    #spider kwargs
    intime = '一天内'  #一天内,一周内,一月内,全部时间
    page_count_limit = 0

    #db_adapter
    db_adapter_cls = BbsMongodbAdapter

    def get_query_request(self, response):
        """
        qihoo未找到能修改每页显示数量的地方
        """
        intime = self.intime
        if intime == '全部时间':
            return super(QihooBbsSpider, self).get_query_request(response)
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
        intime = intime.encode(encoding)
        query_request = br.click_link(text=intime)
        scrapy_request = request_mechanize2scrapy(query_request)
        scrapy_request.callback = self.query_callback
        url = scrapy_request.url
        query = get_url_query(url)
        query['type'] = 'bbs'
        new_url = change_url_query(url, query)
        new_request = scrapy_request.replace(url=new_url)
        return new_request

    info_misc_res = {
        'author': '作者[：:]\s*(\S*)\s*',
        'site_name': '来源[：:]\s*(\S*)\s*',
        'view_count': '浏览[：:]\s*(\S*)\s*',
        'reply_count': '回复[：:]\s*(\S*)\s*',
    }
    info_misc_patterns = {k: re.compile(v) for k, v in info_misc_res.items()}

    def _ana_info_misc(self, hxs):
        result = {}
        for string in hxs.extract():
            for var, p in self.info_misc_patterns.items():
                match = p.search(string)
                if match:
                    value = match.group(1)
                    result[var] = value
        author = result.get('author', '')
        site_name = result.get('site_name', '')
        view_count = result.get('view_count', 0)
        reply_count = result.get('reply_count', 0)
        view_count = try_int_or_0(view_count)
        reply_count = try_int_or_0(reply_count)
        return author, site_name, view_count, reply_count

    def parse_list_page(self, response):
        multi_xpath = '//div[@id="module-list"]/dl'
        html5_response = response_html5parse(response)
        hxs = HtmlXPathSelector(html5_response)
        multi_hxs = hxs.select(multi_xpath)
        for hxs in multi_hxs:
            title = ''.join(hxs.select('./dt[@class="title"]/a//text()').extract())
            pub_time = ''.join(hxs.select('./dt[@class="title"]/span//text()').extract())
            overview = ''.join(hxs.select('./dd[@class="content"]//text()').extract())
            url = ''.join(hxs.select('./dt[@class="title"]/a/@href').extract())
            info_misc_hxs = hxs.select('./dd[@class="info"]//text()')
            author, site_name, view_count, reply_count = self._ana_info_misc(info_misc_hxs)
            url = urllib.unquote(url).strip()
            doc = {
                'data_source': '奇虎论坛搜索',
                'site_name': site_name,
                'title': title,
                'pub_time': pub_time,
                'overview': overview,
                'url': url,
                'author': author,
                'view_count': view_count,
                'reply_count': reply_count,
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