#coding=utf8
#!/usr/bin/env python
"""
wanfang_patent爬虫
cmd:
scrapy crawl wanfang_patent --logfile=/tmp/wanfang_patent.txt
scrapy crawl_ex wanfang_patent --logfile=/tmp/wanfang_patent.txt
"""
from __future__ import division, print_function, unicode_literals
from feet8.pipelines.attachment import get_image_urls

from feet8.spiders.patent.utils import PatentMongodbAdapter, PatentItem, blur_ana_patent


__metaclass__ = type

#Author:wuya @ smallteam
#Date: 13-7-1
import urllib

from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from feet8.cells.leg_spider import LegSpider
from feet8.utils.misc import response_html5parse, fix_possible_missing_scheme, get_mime_type_in_response

#todo temp
from feet8.querys import querys1

class WanfangPatentSpider(LegSpider):
    name = 'wanfang_patent'

    _item = PatentItem()

    querys = querys1
    # querys = ['你好','1']

    entry_url = 'http://c.wanfangdata.com.cn/Patent.aspx'
    #search_form_order = 0
    #search_input_name = 'queryBox'
    next_page_word = '下一页'
    visit_detail = True

    db_adapter_cls = PatentMongodbAdapter

    def get_query_request(self, response):
        #http://s.wanfangdata.com.cn/Patent.aspx?q=%E4%BD%A0%E5%A5%BD&f=c.Patent
        encoding = response.encoding
        query = response.meta['query']
        query = query.encode(encoding)
        url = b'http://s.wanfangdata.com.cn/Patent.aspx?q=%s&f=c.Patent' % query
        request = Request(url)
        # noinspection PyUnresolvedReferences
        request.callback = self.query_callback
        return request

    def parse_list_page(self, response):
        multi_xpath = '//ul[@class="list_ul"]'
        html5_response = response_html5parse(response)
        hxs = HtmlXPathSelector(html5_response)
        multi_hxs = hxs.select(multi_xpath)
        for hxs in multi_hxs:
            url = ''.join(hxs.select('.//a[.//text()="查看详细信息"]/@href').extract())
            # url = ''.join(hxs.select('./li[1]/a[3]/@href').extract())
            patent_name = ''.join(hxs.select('./li[1]/a[3]//text()').extract())

            url = urllib.unquote(url).strip()
            doc = {
                'patent_name': patent_name,
                'data_source': '万方专利搜索',
                'url': url,
            }
            detail_url = fix_possible_missing_scheme(url)
            list_url = response.url
            query = response.meta.get('query')
            if not detail_url:
                next_request = None
            else:
                # detail_url = detail_url.replace('_free', '')
                next_request = Request(detail_url, callback=self.parse_detail_page)
            item = PatentItem(doc=doc,
                              next_request=next_request, list_url=list_url, query=query,
                              attachments=[], attachment_urls=[])
            yield self.item_or_request(item)

    def parse_detail_page(self, response):
        item = response.meta['item']

        html5_response = response_html5parse(response)
        hxs = HtmlXPathSelector(html5_response)

        texts = hxs.select('//table[@id="perildical2_dl"]//text()').extract()
        texts = clean_wanfang_texts(texts)
        result_doc = blur_ana_patent(texts)

        abstract = ''.join(hxs.select('//div[@class="abstracts"]//text()').extract())

        doc = item['doc']
        doc.update(result_doc)
        doc['abstract'] = abstract
        attachments = item['attachments']
        attach1 = {
            'url': response.url,
            'data': response.body_as_unicode(),
            'mime_type': get_mime_type_in_response(response)
        }
        attachments.append(attach1)
        image_urls = get_image_urls(response)
        item['attachment_urls'] += image_urls
        # more_url = response.url.replace('_free', '')
        # next_request = Request(more_url, callback=self.parse_more_page)
        # item['next_request'] = next_request

        #hotfix for patent_type
        patent_type = ''.join(hxs.select('//th[contains(.//text(),"专利类型")]/../td//text()').extract())
        doc['patent_type'] = patent_type

        yield self.item_or_request(item)


def clean_wanfang_texts(texts):
    texts = [text.strip() for text in texts]
    texts = [text.strip(':') for text in texts]
    texts = [text.strip('：') for text in texts]
    texts = [text for text in texts if text]
    return texts