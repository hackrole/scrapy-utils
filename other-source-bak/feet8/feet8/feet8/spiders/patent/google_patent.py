#coding=utf8
#!/usr/bin/env python
"""
google_patent爬虫
cmd:
scrapy crawl google_patent --logfile=/tmp/google_patent.txt
scrapy crawl_ex google_patent --logfile=/tmp/google_patent.txt
"""
from __future__ import division, print_function, unicode_literals
from scrapy.contrib.linkextractors.lxmlhtml import LxmlParserLinkExtractor
from feet8.pipelines.attachment import get_image_urls

from feet8.spiders.patent.utils import PatentMongodbAdapter, PatentItem, blur_ana_patent


__metaclass__ = type

#Author:wuya @ smallteam
#Date: 13-7-1
import urllib

from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from feet8.cells.leg_spider import LegSpider
from feet8.utils.misc import response_html5parse, fix_possible_missing_scheme, get_mime_type_in_response, get_url_query, change_url_query

#todo temp
from feet8.querys import querys1


class GooglePatentSpider(LegSpider):
    name = 'google_patent'

    _item = PatentItem()

    querys = querys1
    # querys = ['你好', '1']

    entry_url = 'http://www.google.com.hk/?tbm=pts'
    search_form_order = 0
    search_input_name = 'q'
    # next_page_word = 'Next'
    next_page_word = '下一頁'

    visit_detail = True

    db_adapter_cls = PatentMongodbAdapter

    def get_query_request(self, response):
        request = super(GooglePatentSpider, self).get_query_request(response)
        url = request.url
        query = get_url_query(url)
        query.pop('btnG')
        query['num'] = '100'
        new_url = change_url_query(url, query)
        new_request = request.replace(url=new_url)
        return new_request

    def parse_list_page(self, response):
        multi_xpath = '//li[@class="g"]'
        html5_response = response_html5parse(response)
        hxs = HtmlXPathSelector(html5_response)
        multi_hxs = hxs.select(multi_xpath)
        for hxs in multi_hxs:
            #//li[@class="g"][1]//h3/a/@href
            url = ''.join(hxs.select('.//h3/a/@href').extract())

            url = urllib.unquote(url).strip()
            doc = {
                'data_source': 'google专利搜索',
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

        texts_hxs = hxs.select('//table[contains(@class,"patent-bibdata")]//tr')
        texts = [''.join(hxs.select('.//text()').extract()) for hxs in texts_hxs]
        # texts = clean_google_texts(texts)
        result_doc = blur_ana_patent(texts)
        classification_hxs = hxs.select('//td[text()="國際專利分類號"]/parent::* | '
                             '//td[text()="国际分类号"]/parent::* |'
                             '//td[text()="International Classification"]/parent::*')
        patent_state = ''.join(hxs.select('//td[text()="出版類型"]/../td[2]//text()').extract())

        texts1 = [''.join(classification_hxs.select('.//text()').extract())]
        result_doc1 = blur_ana_patent(texts1)
        doc = item['doc']
        doc.update(result_doc)
        doc.update(result_doc1)

        patent_name = ''.join(hxs.select('//span[@class="patent-title"]//text()').extract())
        abstract = ''.join(
            hxs.select('//div[@class="patent-section patent-abstract-section"]//div[@class="patent-text"]//text()')
            .extract())
        description = ''.join(
            hxs.select('//div[@class="patent-section patent-description-section"]//div[@class="patent-text"]//text()')
            .extract())
        claims = ''.join(
            hxs.select('//div[@class="patent-section patent-claims-section"]//div[@class="patent-text"]//text()')
            .extract())

        doc['patent_name'] = patent_name
        doc['abstract'] = abstract
        doc['description'] = description
        doc['claims'] = claims
        doc['patent_state'] = patent_state
        doc['patent_type'] = ''

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
        #如果有中文版本，对中文版本进行抓取
        link_ex = LxmlParserLinkExtractor(unique=False)
        links = link_ex.extract_links(response)
        for link in links:
            if link.text in ['Chinese', 'chinese', '中文']:
                request = Request(link.url, callback=self.parse_detail_page)
                doc = {
                    'data_source': 'google专利搜索',
                    'url': link.url,
                }
                cn_item = PatentItem(doc=doc,
                                     next_request=request, list_url=item['list_url'], query=item['query'],
                                     attachments=[], attachment_urls=[])
                yield self.item_or_request(cn_item)
                break