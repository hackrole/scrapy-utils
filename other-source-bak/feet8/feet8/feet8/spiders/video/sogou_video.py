#coding=utf8
#!/usr/bin/env python
"""
sogou_video爬虫
cmd:
scrapy crawl sogou_video --logfile=/tmp/sogou_video.txt
scrapy crawl_ex sogou_video --logfile=/tmp/sogou_video.txt
"""
from __future__ import division, print_function, unicode_literals

from feet8.spiders.video.utils import VideoItem, VideoMongodbAdapter


__metaclass__ = type

#Author:wuya @ smallteam
#Date: 13-7-1
import urllib

from scrapy.selector import HtmlXPathSelector

from feet8.cells.leg_spider import LegSpider
from feet8.utils.misc import response_html5parse, fix_possible_missing_scheme
from feet8.querys import querys1

# _video_item = VideoItem()


class SogouSpider(LegSpider):
    name = 'sogou_video'

    _item_cls = VideoItem

    querys = querys1
    querys = ['你好', '1']

    entry_url = 'http://v.sogou.com/'
    search_form_order = 0
    search_input_name = 'query'
    # next_page_word = 'Next'
    next_page_word = '下一页'

    visit_detail = False

    #spider kwargs
    page_count_limit = 0

    #spider_settings
    custom_settings = {
        # 'DOWNLOAD_DELAY': 0,
    }
    #db_adapter
    db_adapter_cls = VideoMongodbAdapter

    def parse_list_page(self, response):
        multi_xpath = '//ul[@id="vlist1"]/li'
        html5_response = response_html5parse(response)
        hxs = HtmlXPathSelector(html5_response)
        multi_hxs = hxs.select(multi_xpath)
        for hxs in multi_hxs:
            #//li[@class="g"][1]//h3/a/@href
            url = ''.join(hxs.select('.//div/a/@href').extract())
            title = ''.join(hxs.select('.//h3//text()').extract())
            title = title.strip()
            thumb = ''.join(hxs.select('.//div[@class="imgbox"]//img//@src').extract())
            pub_time = ''.join(hxs.select('.//p//text()').extract())
            pub_time = pub_time.lstrip('发布时间：')
            total_time = ''.join(hxs.select('.//span[@class="updatetxt_time"]//text()').extract())
            from_site = ''.join(hxs.select('.//div[@class="updatetxt"]/text()').extract())
            url = urllib.unquote(url).strip()
            url = fix_possible_missing_scheme(url)
            doc = {
                'data_source': 'sogou视频搜索',
                'url': url,
                'title': title,
                'thumb': thumb,
                'pub_time': pub_time,
                'total_time': total_time,
                'from_site': from_site,
            }
            list_url = response.url
            query = response.meta.get('query')
            next_request = None
            attachment_urls = []
            if thumb:
                attachment_urls.append(thumb)
            item = VideoItem(doc=doc,
                             next_request=next_request, list_url=list_url, query=query,
                             attachments=[], attachment_urls=attachment_urls)
            yield self.item_or_request(item)

    # def is_duplicate_request(self, request):
    #     if self._no_duplicate_request:
    #         return self.db_adapter.is_duplicate_request(request, _video_item)
    #     else:
    #         return False
