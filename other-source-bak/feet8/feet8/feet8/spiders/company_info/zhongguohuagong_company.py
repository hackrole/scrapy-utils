#coding=utf8
#!/usr/bin/env python
"""


全球五金 商家信息
cmd:
scrapy crawl zhongguohuagong_company_spider --logfile=/tmp/zhongguohuagong_company.txt
oop

"""

from __future__ import division, print_function, unicode_literals


__metaclass__ = type

#Author:wuya @ smallteam
#Date: 13-5-17
import os

import urllib

from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from feet8.items import LegItem
from feet8.cells.leg_spider import LegSpider
from feet8.utils.misc import response_html5parse
from feet8.utils import fnvhash

from .spider_utils import clean_string, parse_contact, parse_products, process_company_item, save_company_item

class zhongguohuagongCompanySpider(LegSpider):
    name = 'zhongguohuagong_company_spider'
    querys = ['淄博']
    entry_url = 'http://china.chemnet.com/company/'
    search_form_order = 0
    search_input_name = 'terms'
    #翻页不可用
    #next_page_word = '>>'

    visit_detail = True
    #db
    collection = 'shop_info'
    #shop
    shop_site_type = '中国化工'
    #validate
    item_doc_length = 24
    #spider_kwargs

    def __init__(self, *args, **kwargs):
        self._total_page = None
        self._get_next_page_request_called = False
        super(zhongguohuagongCompanySpider, self).__init__(*args, **kwargs)

    def get_next_page_request(self, response):
        html5_response = response_html5parse(response)
        page_hxs = HtmlXPathSelector(html5_response)
        if not self._total_page:
            total_page = ''.join(page_hxs.select('//div[@id="tc_menu"]/div[2]/span[2]//text()').extract())
            try:
                self._total_page = int(total_page)
            except ValueError:
                self._total_page = 0
        sub_url = ''.join(page_hxs.select('//div[@id="tc_menu"]/div[2]/a[1]/@href').extract())
        base_url = 'http://china.chemnet.com/company'
        page_num = response.meta['page_num']
        if page_num < self._total_page - 1:
            p = page_num + 1
            url = os.path.join(base_url, sub_url)
            #fast hack
            url = url.replace(';p=', '', 1)
            url += ';p=%d' % p
            return Request(url, callback=self.query_callback)

    def parse_list_page(self, response):
        """
        """
        multi_xpath = '//div[@class="tc_qytitle1"]'
        html5_response = response_html5parse(response)
        page_hxs = HtmlXPathSelector(html5_response)
        multi_hxs = page_hxs.select(multi_xpath)
        for hxs in multi_hxs:
            #提取部分
            shop_name = ''.join(hxs.select('./div/dl/dt/a//text()').extract())
            shop_name = clean_string(shop_name)
            shop_site_url = ''.join(hxs.select('./div/dl/dt/a/@href').extract())
            shop_site_url = urllib.unquote(shop_site_url).strip()
            detail_url = os.path.join(shop_site_url, 'clist--.html')

            doc = {
                'shop_name': shop_name.strip(),
                'shop_site_url': shop_site_url.strip(),
                'detail_url': detail_url,
            }

            query = response.meta['query']
            list_url = response.url

            if not shop_site_url:
                next_request = None
            else:
                headers = {
                    'referer': shop_site_url
                }
                next_request = Request(detail_url, headers=headers, callback=self.parse_detail_page)
            item = LegItem(collection=self.collection, doc=doc,
                           next_request=next_request, list_url=list_url, query=query)
            yield self.item_or_request(item)

    def parse_detail_page(self, response):
        item = response.meta['item']
        doc = item['doc']
        html5_response = response_html5parse(response)
        page_hxs = HtmlXPathSelector(html5_response)

        contact_hxs = page_hxs.select('//div[@id="contrt"]/div[1]/dl/dd[1]/table//td//text()')
        contact_dic = parse_contact(contact_hxs)

        shop_products_hxs = page_hxs.select('//div[@id="tdsub_1"]//text()')
        shop_products_hxs = shop_products_hxs[3:]
        shop_products = parse_products(shop_products_hxs)

        doc.update(contact_dic)
        doc['shop_products'] = shop_products.strip()

        yield self.item_or_request(item)

    def process_item(self, item):
        process_company_item(item, self)

    def save_item(self, item):
        save_company_item(item)