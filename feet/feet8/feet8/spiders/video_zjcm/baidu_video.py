#coding=utf8
#!/usr/bin/env python
"""
baidu_video爬虫
cmd:
scrapy crawl baidu_video --logfile=/tmp/baidu_video.txt
scrapy crawl_ex baidu_video --logfile=/tmp/baidu_video.txt
"""
from __future__ import division, print_function, unicode_literals
import copy
import json
from scrapy.http import Request

from feet8.spiders.video_zjcm.utils import VideoZjcmItem, VideoMongodbAdapter


__metaclass__ = type

#Author:wuya @ smallteam
#Date: 13-7-16


from scrapy.selector import HtmlXPathSelector

from feet8.cells.leg_spider import LegSpider
from feet8.utils.misc import response_html5parse, get_url_query


class BaiduVideoZjcmSpider(LegSpider):
    name = 'baidu_video_zjcm'

    _item = VideoZjcmItem()

    querys = ['你好', '1', '中国好声音']
    #todo temp
    from feet8.querys import querys_zjcm as querys
    querys = querys

    entry_url = 'http://video.baidu.com/'
    search_form_order = 0
    search_input_name = 'word'

    next_page_word = '没有下一页'

    db_adapter_cls = VideoMongodbAdapter

    def parse_list_page(self, response):

        multi_xpath = '//div[@class="special-area-cont"]/div'
        html5_response = response_html5parse(response)
        hxs = HtmlXPathSelector(html5_response)
        multi_hxs = hxs.select(multi_xpath)
        query = response.meta.get('query')
        for hxs in multi_hxs:
            #//li[@class="g"][1]//h3/a/@href
            title = ''.join(hxs.select('.//h3//text()').extract()).strip()
            _video_name = ''.join(hxs.select('.//h3//span//font//text()').extract())
            if _video_name != query:
                continue
            url = ''.join(hxs.select('.//h3//a/@href').extract())
            _id = get_url_query(url)['id']
            doc = {
                'data_source': 'baidu视频搜索',
                'url': url,
                'title': title,
                'id': _id,
            }
            list_url = response.url
            json_list_url = 'http://video.baidu.com/htvshowsingles/?id=%s' % _id
            next_request = Request(json_list_url, callback=self.parse_site_list)
            item = VideoZjcmItem(doc=doc,
                                 next_request=next_request, list_url=list_url, query=query,
                                 attachments=[], attachment_urls=[])
            yield self.item_or_request(item)

    def parse_site_list(self, response):
        json_result = json.loads(response.body_as_unicode())
        if not json_result:
            return
        for site in json_result['sites']:
            site_url = site['site_url']
            site_name = site['site_name']
            item = response.meta['item']
            #todo check
            item = copy.deepcopy(item)
            doc = item['doc']
            _id = doc['id']
            detail_url = "http://video.baidu.com/htvshowsingles/?id=%s&site=%s" % (_id, site_url)
            doc['site_url'] = site_url
            doc['site_name'] = site_name
            next_request = Request(detail_url, callback=self.parse_site)
            item['next_request'] = next_request
            yield self.item_or_request(item)

    def parse_site(self, response):
        json_result = json.loads(response.body_as_unicode())
        if not json_result:
            return
        for video in json_result['videos']:
            video_url = video['url']
            main_title = video['work_title'].strip()
            sub_title = video['title'].strip()
            episode = video['episode']

            item = response.meta['item']
            #todo check
            item = copy.deepcopy(item)
            doc = item['doc']
            doc['url'] = video_url
            doc['main_title'] = main_title
            doc['sub_title'] = sub_title
            doc['episode'] = episode

            doc.pop('id')

            next_request = None
            item['next_request'] = next_request
            yield self.item_or_request(item)