#coding=utf8
#!/usr/bin/env python
"""
baidu_news爬虫
cmd:
scrapy crawl baidu_news_spider --logfile=/tmp/baidu_news.txt
scrapy crawl_ex baidu_news_spider --logfile=/tmp/baidu_news.txt
"""
from __future__ import division, print_function, unicode_literals




__metaclass__ = type

#Author:wuya @ smallteam
#Date: 13-5-16
import datetime
import urllib
import time

from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from feet8.utils.form import activate_controls
from feet8.cells.leg_spider import LegSpider
from feet8.utils.multi_convert import response_scrapy2mechanize, request_mechanize2scrapy
from feet8.utils.misc import response_html5parse, fix_possible_missing_scheme, is_duplicate_request_by_url
from feet8.spiders.news.utils import NewsItem, NewsMongodbAdapter


class BaiduNewsSpider(LegSpider):
    name = 'baidu_news'

    querys = ['你好','今天']

    entry_url = 'http://news.baidu.com/advanced_news.html'
    search_form_order = 0
    search_input_name = 'q1'
    next_page_word = '下一页>'
    visit_detail = True

    #spider kwargs
    item_count_per_page = b'100'
    page_count_limit = 0
    begin_date = ''
    end_date = ''
    interval_days = 0

    #spider_settings
    custom_settings = {
        # 'DOWNLOAD_DELAY': 0,
    }
    #db_adapter
    db_adapter_cls = NewsMongodbAdapter

    # noinspection PyUnresolvedReferences
    def __init__(self, *args, **kwargs):
        """
        begin_date:开始日期,like 2013-5-16
        end_date:结束日期,like 2013-12-1
        都为空时不使用时间限制查询
        """
        super(BaiduNewsSpider, self).__init__(*args, **kwargs)
        self._cal_begin_end_date()

    def _cal_begin_end_date(self):
        if self.begin_date or self.end_date:
            return
        else:
            if self.interval_days is not None:
                end = datetime.datetime.today()
                begin = end - datetime.timedelta(days=self.interval_days)
                self.begin_date = '%s-%s-%s' % (begin.year, begin.month, begin.day)
                self.end_date = '%s-%s-%s' % (end.year, end.month, end.day)
                return

    def get_query_request(self, response):
        """
        填表单,构造相应请求
        """
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
        br[b'rn'] = [self.item_count_per_page]
        activate_controls(br.form)
        if not self.begin_date and not self.end_date:
            br[b's'] = [b'1']
            br[b'begin_date'] = b''
            br[b'end_date'] = b''
        else:
            br[b's'] = [b'2']
            br[b'begin_date'] = self.begin_date.encode(encoding)
            br[b'end_date'] = self.end_date.encode(encoding)
            y0, m0, d0 = self.begin_date.split('-')
            y1, m1, d1 = self.end_date.split('-')
            br[b'y0'] = y0.encode(encoding)
            br[b'm0'] = m0.encode(encoding)
            br[b'd0'] = d0.encode(encoding)
            br[b'y1'] = y1.encode(encoding)
            br[b'm1'] = m1.encode(encoding)
            br[b'd1'] = d1.encode(encoding)
            br[b'bt'] = str(int(time.mktime(time.strptime(self.begin_date, '%Y-%m-%d'))))
            br[b'et'] = str(int(time.mktime(time.strptime(self.end_date, '%Y-%m-%d'))))
        query_request = br.click()
        scrapy_request = request_mechanize2scrapy(query_request)
        scrapy_request.callback = self.query_callback
        return scrapy_request

    def parse_list_page(self, response):
        multi_xpath = '//*[@id="r"]/table'
        html5_response = response_html5parse(response)
        hxs = HtmlXPathSelector(html5_response)
        multi_hxs = hxs.select(multi_xpath)
        for hxs in multi_hxs:
            site_name, pub_time = ''.join(hxs.select('.//nobr//text()').extract()).split(' ', 1)
            title = ''.join(hxs.select('.//span/b//text()').extract())
            overview = ''.join(hxs.select('.//font[@size="-1"]//text()').extract())
            url = ''.join(hxs.select('.//span/../@href').extract())
            url = urllib.unquote(url).strip()
            doc = {
                'data_source': '百度新闻搜索',
                'site_name': site_name,
                'pub_time': pub_time,
                'title': title,
                'overview': overview,
                'url': url,
            }
            detail_url = fix_possible_missing_scheme(url)
            list_url = response.url
            query = response.meta.get('query')
            if not detail_url:
                next_request = None
            else:
                next_request = Request(detail_url, callback=self.parse_detail_page)
            item = NewsItem(doc=doc,
                            next_request=next_request, list_url=list_url, query=query)
            yield self.item_or_request(item)

    def parse_detail_page(self, response):
        item = response.meta['item']
        item['doc']['detail_pages'] = [response.body_as_unicode()]
        yield self.item_or_request(item)

    def is_duplicate_request(self, request):
        if self._no_duplicate_request:
            return self.db_adapter.is_duplicate_request(request, NewsItem())
        else:
            return False


