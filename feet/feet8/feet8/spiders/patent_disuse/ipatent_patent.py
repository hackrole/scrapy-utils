#coding=utf8
#!/usr/bin/env python
"""
未完成,这货的翻页用了viewstate-.-要模拟出来得研究下asp.net的viewstate机制-.-
ipatent_patent爬虫
cmd:
scrapy crawl ipatent_patent --logfile=/tmp/ipatent_patent.txt
scrapy crawl_ex ipatent_patent --logfile=/tmp/ipatent_patent.txt
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

class IpatentPatentSpider(LegSpider):
    name = 'ipatent_patent'

    # querys = querys1
    querys = ['你好','1',]

    entry_url = 'http://so.5ipatent.com/'
    # search_form_order = 0
    # search_input_name = 'searchContent'
    next_page_word = '下一页'
    visit_detail = True

    db_adapter_cls = PatentMongodbAdapter

    def get_query_request(self, response):

        pass

    def parse_list_page(self, response):
        multi_xpath = '//table[@id]'
        html5_response = response_html5parse(response)
        hxs = HtmlXPathSelector(html5_response)
        multi_hxs = hxs.select(multi_xpath)
        for hxs in multi_hxs:
            url = ''.join(hxs.select('.//a/@href').extract())
            url = urllib.unquote(url).strip()
            doc = {
                'data_source': '百度专利搜索',
                'url': url,
            }
            detail_url = fix_possible_missing_scheme(url)
            list_url = response.url
            query = response.meta.get('query')
            if not detail_url:
                next_request = None
            else:
                next_request = Request(detail_url, callback=self.parse_detail_page)
            item = PatentItem(doc=doc,
                              next_request=next_request, list_url=list_url, query=query,
                              attachments=[], attachment_urls=[])
            yield self.item_or_request(item)

    def parse_detail_page(self, response):
        item = response.meta['item']

        html5_response = response_html5parse(response)
        hxs = HtmlXPathSelector(html5_response)

        texts1 = hxs.select('//table[@class="tb"]//td//text()').extract()
        texts2 = hxs.select('//div[@class="t2"]//text()').extract()
        result_doc1 = blur_ana_patent(texts1)
        result_doc2 = blur_ana_patent(texts2)
        patent_name = ''.join(hxs.select('//div[@class="t1"]//text()').extract())
        abstract = ''.join(hxs.select('//div[@class="con2"]//text()').extract())

        doc = item['doc']
        doc.update(result_doc1)
        doc.update(result_doc2)
        doc['patent_name'] = patent_name
        doc['abstract'] = abstract
        doc['application_number'] = doc['application_number'].lstrip('/专利号： ')
        attachments = item['attachments']
        attach1 = {
            'url': response.url,
            'data': response.body_as_unicode(),
            'mime_type': get_mime_type_in_response(response)
        }
        attachments.append(attach1)
        image_urls = get_image_urls(response)
        item['attachment_urls'] += image_urls
        yield self.item_or_request(item)

    def is_duplicate_request(self, request):
        if self._no_duplicate_request:
            return self.db_adapter.is_duplicate_request(request, PatentItem())
        else:
            return False


