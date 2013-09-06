#coding=utf8
#!/usr/bin/env python
"""
caiban_sina_weibo
cmd:
scrapy crawl caiban_sina_weibo --logfile=/tmp/caiban_sina_weibo.txt
"""
from __future__ import division, print_function, unicode_literals

__metaclass__ = type

#Author:wuya @ smallteam
#Date: 13-5-16
import os
import urllib
import re

from urlparse2 import urlparse, urlunparse

from scrapy.selector import HtmlXPathSelector
from feet8.cells.leg_spider import LegSpider
from feet8.utils.misc import response_html5parse, get_url_query, try_int_or_0, cal_begin_end_date
from feet8.spiders.weibo.utils import WeiboItem, WeiboMongodbAdapter


querys2 =\
['中国梦想秀',
'非诚勿扰',
'非你莫属',
'舌尖上的中国',
'中国好声音 华少',
'CCTV 新闻联播',
'周立波',
'真人秀',
'温州',
'星跳水立方',
'中国星跳跃',
'百里挑一',
'农夫山泉新闻发布会',
'农夫山泉',
'微信',
'动物世界',
'新闻1+1',
'厦门BRT',
'周立波 中国梦想秀',
'进击的巨人 艾伦',
'中国最强音',
'进击的巨人',
'艾伦',
'三爷',
'中国梦-之声',]

class CaibanSinaWeibo(LegSpider):
    name = 'caiban_sina_weibo'




    querys = querys2
    page_count_limit = 10

    entry_url = 'http://weibo.cn/search/'
    search_form_order = 0
    search_input_name = 'keyword'
    next_page_word = '下页'
    visit_detail = False

    #spider kwargs
    sort = 'time'
    begin_date = None
    end_date = None
    interval_days = 0

    #spider_settings
    custom_settings = {
        # 'DOWNLOAD_DELAY': 0,
    }
    #db_adapter
    db_adapter_cls = WeiboMongodbAdapter

    # noinspection PyUnresolvedReferences
    def __init__(self, *args, **kwargs):
        super(CaibanSinaWeibo, self).__init__(*args, **kwargs)

    def _get_msg_id_from_url(self, url):
        msg_id = ''
        try:
            msg_id = os.path.split(urlparse(url).path)[1]
        finally:
            return msg_id

    def _get_user_id_from_url(self, url):
        return get_url_query(url).get('uid', '')

    def _get_user_id(self, hxs):
        urls = hxs.extract()
        own = self._get_user_id_from_url(urls[-1])
        if len(urls) == 2:
            forward = self._get_user_id_from_url(urls[0])
        else:
            forward = ''
        return own, forward

    def _get_msg_id(self, hxs):
        urls = hxs.extract()
        own = self._get_msg_id_from_url(urls[-1])
        if len(urls) == 2:
            forward = self._get_msg_id_from_url(urls[0])
        else:
            forward = ''
        return own, forward

    misc1_res = {
        'zan_count': '^赞\[(\d*)\]',
        'zhuanfa_count': '^转发\[(\d*)\]',
        'pinglun_count': '^评论\[(\d*)\]',
    }
    misc1_patterns = {k: re.compile(v) for k, v in misc1_res.items()}

    def _ana_misc1(self, hxs):
        result = {}
        for string in hxs.extract():
            for var, p in self.misc1_patterns.items():
                match = p.search(string)
                if match:
                    value = match.group(1)
                    result[var] = value
                    break
        zan = result.get('zan_count', 0)
        zhuanfa = result.get('zhuanfa_count', 0)
        pinglun = result.get('pinglun_count', 0)
        zan = try_int_or_0(zan)
        zhuanfa = try_int_or_0(zhuanfa)
        pinglun = try_int_or_0(pinglun)
        return zan, zhuanfa, pinglun

    def _ana_misc2(self, hxs):
        misc2 = ''.join(hxs.extract())
        time_info, from_info = misc2.split('来自')
        time = time_info
        return time, from_info

    def get_query_request(self, response):
        request = super(CaibanSinaWeibo, self).get_query_request(response)
        begin_date, end_date = cal_begin_end_date(self.begin_date, self.end_date, self.interval_days)
        starttime = begin_date.strftime('%Y%m%d')
        endtime = end_date.strftime('%Y%m%d')
        sort = self.sort
        append_query = urllib.urlencode({'starttime': starttime, 'endtime': endtime, 'sort': sort})
        new_body = '%s&%s' % (request.body, append_query)
        new_request = request.replace(body=new_body)
        return new_request

    def parse_list_page(self, response):
        multi_xpath = '/html/body/div[@id and @class="c"]'
        html5_response = response_html5parse(response)
        hxs = HtmlXPathSelector(html5_response)
        multi_hxs = hxs.select(multi_xpath)
        list_url = response.url
        query = response.meta.get('query')
        for hxs in multi_hxs:
            nick = ''.join(hxs.select('./div[1]/a//text()').extract())
            user_url = ''.join(hxs.select('./div[1]/a/@href').extract())
            user_url = urllib.unquote(user_url).strip()
            user_url_up = urlparse(user_url)
            user_url_up.query = ''
            user_url = urlunparse(user_url_up)
            div3 = hxs.select('./div[3]')
            if div3:
                content = ''.join(div3.select('.//text()').extract()[1:-10])
            else:
                content = ''.join(hxs.select('./div[1]/span//text()').extract())
            misc1 = hxs.select('.//a//text()')
            zan_count, zhuanfa_count, pinglun_count = self._ana_misc1(misc1)
            misc2 = hxs.select('.//span[@class="ct"]//text()')
            time, from_info = self._ana_misc2(misc2)
            misc3 = hxs.select('.//a[@class="cc"]/@href')
            own_msg_id, forward_msg_id = self._get_msg_id(misc3)
            own_user_id, forward_user_id = self._get_user_id(misc3)
            if forward_msg_id and forward_user_id:
                is_forward = True
                forward_msg_url1 = 'http://weibo.com/%s/%s' % (forward_user_id, forward_msg_id)
                forward_msg_url2 = 'http://weibo.cn/%s/%s' % (forward_user_id, forward_msg_id)
            else:
                is_forward = False
                forward_msg_url1 = ''
                forward_msg_url2 = ''
            doc = {
                'data_source': '新浪微博搜索',
                'nick': nick,
                'user_url': user_url,
                'content': content,
                'zan_count': zan_count,
                'zhuanfa_count': zhuanfa_count,
                'pinglun_count': pinglun_count,
                'time': time,
                'from_info': from_info,
                'own_user_id': own_user_id,
                'own_msg_id': own_msg_id,
                'own_msg_url1': 'http://weibo.com/%s/%s' % (own_user_id, own_msg_id),
                'own_msg_url2': 'http://weibo.cn/%s/%s' % (own_user_id, own_msg_id),
                'forward_user_id': forward_user_id,
                'forward_msg_id': forward_msg_id,
                'forward_msg_url1': forward_msg_url1,
                'forward_msg_url2': forward_msg_url2,
                'is_forward': is_forward,
                'sort': self.sort,
            }
            #暂不处理weibo用户的首页头像
            # user_homepage = user_url
            # if not user_homepage:
            #     next_request = None
            # else:
            #     next_request = Request(user_homepage, callback=self.parse_user_homepage)
            item = WeiboItem(doc=doc,
                             next_request=None, list_url=list_url, query=query)
            yield self.item_or_request(item)

    #暂不处理weibo用户的首页头像
    # def parse_user_homepage(self, response):
    #     item = response.meta['item']
    #     item['doc']['detail'] = response.body_as_unicode()
    #     yield self.item_or_request(item)