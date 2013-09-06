#coding=utf8
#!/usr/bin/env python
"""
baidu_weibo爬虫
cmd:
scrapy crawl baidu_weibo_spider --logfile=/tmp/baidu_weibo.txt
"""
from __future__ import division, print_function, unicode_literals

__metaclass__ = type

#Author:wuya @ smallteam
#Date: 13-5-13

import urllib

from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from feet8.cells.leg_spider import LegSpider
# from feet8.items import LegItem
from feet8.utils.misc import response_html5parse,extract_number


def url_clean(url):
    if url.startswith('http://weibo.com'):
        url = url.rstrip('?type=comment')
    return url

class BaiduWeiboSpider(LegSpider):
    name = 'baidu_weibo_spider'
    querys = ['你好']
    entry_url = 'http://www.baidu.com/s?tn=baiduwb&rtt=2&cl=2&rn=20&ie=utf-8&bs=%E4%BD%9B%E5%B1%B1&f=8&rsv_bp=1&wd=%E7%9A%87%E5%AE%B6%E9%A9%AC%E5%BE%B7%E9%87%8C%E8%B6%85%E7%BA%A7%E5%8E%89%E5%AE%B3%E6%97%A0%E6%95%8C&inputT=9734'
    search_form_order = 0
    search_input_name = 'wd'
    next_page_word = '下一页>'
    page_count_limit = 2
    visit_detail = False
    data_type = 10

    def __init__(self, *args, **kwargs):
        super(BaiduWeiboSpider, self).__init__(*args, **kwargs)

    def parse_list_page(self, response):
        multi_xpath = '//*[@id="weibo"]/li'
        html5_response = response_html5parse(response)
        hxs = HtmlXPathSelector(html5_response)
        multi_hxs = hxs.select(multi_xpath)
        for hxs in multi_hxs:
            #
            #user_nick = ''.join(hxs.select('.//a[@name="weibo_rootnick"]/text()').extract())
            #user_url = ''.join(hxs.select('.//a[@name="weibo_rootnick"]/@href').extract())
            # at_users = []
            # for at_user_hxs in hxs.select('.//a[@name="weibo_nick"]'):
            #     #@Riffraff雞東
            #     at_user_nick = at_user_hxs.select('./text()')
            #     #http://weibo.com/n/Riffraff雞東
            #     at_user_url = at_user_hxs.select('./@href')
            #     at_users.append((at_user_nick,at_user_url))
            #3分钟前 - 新浪微博
            pubtime, site_name = ''.join(hxs.select('.//div[@class="m"]/text()').extract()).split(' - ', 1)
            #wait todo change pubtime
            pubtime = None
            title = None
            # ：我还是大大方方的告诉
            # 了 私信太麻烦了。就是他爱我 我不爱他 她爱他 他不爱她 她爱他 她的他爱我 我爱她爱她的他 懂了吗.?
            #todo fix it
            #content是否抓取@
            #content = ''.join(hxs.select('./div/text()').extract())
            #http://weibo.com/2440278962/zwZ7p6yUK?type=comment
            url = ''.join(hxs.select('.//a[@name="weibo_ping"]/@href').extract())
            url = url_clean(url)
            #评论(0)
            comment_count = ''.join(hxs.select('.//a[@name="weibo_ping"]/text()').extract())
            comment_count = extract_number(comment_count)
            #转发(0)
            repost_count = ''.join(hxs.select('.//a[@name="weibo_trans"]/text()').extract())
            repost_count = extract_number(repost_count)

            #todo datatype
            url = urllib.unquote(url).strip()
            doc = {
                'site_name': site_name,
                'title': title,
                'pubtime': pubtime,
                #todo'content': content,
                'url': url,
                'reply_num': comment_count,
                'retweet_num': repost_count,
                'data_type': self.data_type
            }
            detail_url = url
            list_url = response.url
            query = response.meta.get('query')
            item = LegItem(collection='web_data', doc=doc,
                              detail_url=detail_url, list_url=list_url, query=query)
            if detail_url and self.visit_detail:
                detail_request = Request(detail_url, callback=self.parse_detail_page)
                detail_request.meta['item'] = item
                detail_request.meta['query'] = query
                yield detail_request
            else:
                yield item

    def parse_detail_page(self, response):
        item = response.meta['item']
        item['doc']['detail'] = response.body_as_unicode()
        yield item