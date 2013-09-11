#coding=utf8
#!/usr/bin/env python
"""
makepolo 商家信息
cmd:
scrapy crawl makepolo_company_spider --logfile=/tmp/makepolo_company.txt
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type

#Author:wuya @ smallteam
#Date: 13-5-17

import urllib
import os

from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from feet8.items import LegItem
from feet8.cells.leg_spider import LegSpider
from feet8.utils.misc import response_html5parse, get_url_query, change_url_query
from feet8.utils import fnvhash

from .spider_utils import save_company_item, parse_products, parse_contact1, parse_contact2, process_company_item, clean_string


class makepoloCompanySpider(LegSpider):
    name = 'makepolo_company_spider'
    querys = ['淄博']
    entry_url = 'http://caigou.makepolo.com/scw.php?q=query&search_flag=q1'
    # 搜索不可用
    # search_form_order = 0
    # search_input_name = ''
    next_page_word = '下一页 >'

    visit_detail = True
    #db
    collection = 'shop_info'
    #shop
    shop_site_type = '马可波罗'
    #validate
    item_doc_length = 24

    def __init__(self, *args, **kwargs):
        super(makepoloCompanySpider, self).__init__(*args, **kwargs)

    def init(self):
        return self._detect_site_default_encoding()

    def get_entry_request(self, query):
        url_query = get_url_query(self.entry_url)
        url_query['q'] = query.encode(self._site_default_encoding)
        new_url = change_url_query(self.entry_url, url_query)
        headers = {
            'referer': 'http://china.makepolo.com/',
        }
        meta = {
            'query': query,
            'page_num': 0,
        }
        request = Request(url=new_url, headers=headers, callback=self.query_callback, meta=meta)
        return request

    def parse_list_page(self, response):
        multi_xpath = '//div[@class="product_list"]'
        html5_response = response_html5parse(response)
        page_hxs = HtmlXPathSelector(html5_response)
        multi_hxs = page_hxs.select(multi_xpath)
        for hxs in multi_hxs:
            shop_name = ''.join(hxs.select('./div[@class="product_top"]//a//text()').extract())
            shop_name = clean_string(shop_name)
            shop_site_url = ''.join(hxs.select('./div[@class="product_top"]//a/@href').extract())
            shop_site_url = urllib.unquote(shop_site_url).strip()
            about_url = os.path.join(shop_site_url, 'corp/corp.html')
            contact_url = os.path.join(shop_site_url, 'contact_us.html')

            doc = {
                'shop_name': shop_name,
                'shop_site_url': shop_site_url,
                'about_url': about_url,
                'contact_url': contact_url,
            }

            query = response.meta['query']
            list_url = response.url
            if not shop_site_url:
                next_request = None
            else:
                next_request = Request(about_url, callback=self.parse_about_page)
            item = LegItem(collection=self.collection, doc=doc,
                           next_request=next_request, list_url=list_url, query=query)
            yield self.item_or_request(item)

    def parse_about_page(self, response):
        item = response.meta['item']
        doc = item['doc']
        html5_response = response_html5parse(response)
        page_hxs = HtmlXPathSelector(html5_response)

        shop_products_hxs = page_hxs.select('//div[@class="yellowpage_right"]/div[@class="right_mode"]//text()')
        shop_products = parse_products(shop_products_hxs)
        shop_launch_time = ''.join(page_hxs.select('/html/body/div[2]/div[4]/div[2]/div[4]/div[2]/div[1]/ul/li[1]//text()').extract())
        shop_launch_time = shop_launch_time.strip().lstrip('成立时间:：')
        doc['shop_products'] = shop_products
        doc['shop_launch_time'] = shop_launch_time

        contact_url = doc.get('contact_url', '')
        if not contact_url:
            next_request = None
        else:
            next_request = Request(contact_url, callback=self.parse_contact_page)
        item['next_request'] = next_request
        yield self.item_or_request(item)

    def parse_contact_page(self, response):
        item = response.meta['item']
        doc = item['doc']

        html5_response = response_html5parse(response)
        page_hxs = HtmlXPathSelector(html5_response)

        contact_dic = {}
        contact1_hxs = page_hxs.select('//div[@class="com_contact"]/text()')
        contact1_dic = parse_contact1(contact1_hxs)
        contact2_hxs = page_hxs.select('//div[@class="com_contact"]//span//text()')
        contact2_dic = parse_contact2(contact2_hxs)

        contact_dic.update(contact2_dic)
        contact_dic.update(contact1_dic)

        doc.update(contact_dic)

        yield self.item_or_request(item)

    def process_item(self, item):
        process_company_item(item, self)

    def save_item(self, item):
        save_company_item(item)