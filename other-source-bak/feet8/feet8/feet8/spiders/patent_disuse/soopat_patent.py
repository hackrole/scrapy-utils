#coding=utf8
#!/usr/bin/env python
"""
频率限制的非常厉害-.-
soopat_patent爬虫
cmd:
scrapy crawl soopat_patent --logfile=/tmp/soopat_patent.txt
scrapy crawl_ex soopat_patent --logfile=/tmp/soopat_patent.txt
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
from feet8.utils.misc import response_html5parse,  get_mime_type_in_response

#todo temp


class SoopatPatentSpider(LegSpider):
    name = 'soopat_patent'

    querys = ['你好','1']
    # from feet8.querys import querys1
    # querys = querys1

    entry_url = 'http://www.soopat.com/'
    search_form_order = 0
    search_input_name = 'SearchWord'
    next_page_word = '下一页'
    visit_detail = True

    db_adapter_cls = PatentMongodbAdapter

    def parse_list_page(self, response):
        multi_xpath = '//div[@class="PatentBlock"]'
        html5_response = response_html5parse(response)
        hxs = HtmlXPathSelector(html5_response)
        multi_hxs = hxs.select(multi_xpath)

        for hxs in multi_hxs:
            url = ''.join(hxs.select('./div[2]/h2/a/@href').extract())
            url = 'http://www2.soopat.com%s' % url
            url = urllib.unquote(url).strip()
            doc = {
                'data_source': 'soopat中国专利搜索',
                'url': url,
            }
            detail_url = url
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

        texts1 = hxs.select('//span[@class="detailtitle"]//text()').extract()
        texts2 = hxs.select('//table[@class="datainfo"]//text()').extract()
        texts3 = hxs.select('//table[@id="PatentContentTable"]//text()').extract()
        texts1 = clean_soopat_texts(texts1)
        texts2 = clean_soopat_texts(texts2)
        texts3 = clean_soopat_texts(texts3)
        result_doc1 = blur_ana_patent(texts1)
        result_doc2 = blur_ana_patent(texts2)
        result_doc3 = blur_ana_patent(texts3)
        patent_name = ''.join(hxs.select('//span[@class="detailtitle"]/h1//text()').extract())
        abstract = ''.join(hxs.select('//td[@class="sum f14"]//text()').extract())

        doc = item['doc']
        doc.update(result_doc1)
        doc.update(result_doc2)
        doc.update(result_doc3)
        doc['patent_name'] = patent_name
        doc['abstract'] = abstract
        attachments = item['attachments']
        attach1 = {
            'url': response.url,
            'data': response.body_as_unicode(),
            'mime_type': get_mime_type_in_response(response)
        }
        attachments.append(attach1)
        image_urls = get_image_urls(response)
        img_url = ''.join(hxs.select('//a[@class="jqzoom"]/@href').extract())
        image_urls.append(img_url)
        item['attachment_urls'] += image_urls
        yield self.item_or_request(item)

    def is_duplicate_request(self, request):
        if self._no_duplicate_request:
            return self.db_adapter.is_duplicate_request(request, PatentItem())
        else:
            return False

def clean_soopat_texts(texts):
    texts = [text.strip() for text in texts]
    texts = [text for text in texts if text]
    return texts

