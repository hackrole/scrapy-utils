#coding=utf8
#!/usr/bin/env python
"""


中国玻璃 商家信息
cmd:
scrapy crawl zhongguoboli_company_spider --logfile=/tmp/zhongguoboli_company.txt
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

from .spider_utils import save_company_item, clean_string, parse_products, parse_contact, process_company_item

class zhongguoboliCompanySpider(LegSpider):
    name = 'zhongguoboli_company_spider'
    querys = ['淄博']
    entry_url = 'http://www.glass.com.cn/glasscompany/'
    search_form_order = 0
    search_input_name = 'keyword'
    next_page_word = '下一页'

    visit_detail = True
    #db
    collection = 'shop_info'
    #shop
    shop_site_type = '中国玻璃'
    #validate
    item_doc_length = 24
    #spider_kwargs

    def __init__(self, *args, **kwargs):
        super(zhongguoboliCompanySpider, self).__init__(*args, **kwargs)

    def parse_list_page(self, response):
        multi_xpath = '//div[@class="xia_xuxian list_tiao"]'
        html5_response = response_html5parse(response)
        page_hxs = HtmlXPathSelector(html5_response)
        multi_hxs = page_hxs.select(multi_xpath)
        for hxs in multi_hxs:
            shop_name = ''.join(hxs.select('.//ul[@class="list_link"]/li/a//text()').extract())
            shop_name = clean_string(shop_name)
            shop_site_url = ''.join(hxs.select('.//ul[@class="list_link"]/li/a/@href').extract())
            shop_site_url = urllib.unquote(shop_site_url).strip()
            about_url = os.path.join(shop_site_url, 'profile.html')
            contact_url = os.path.join(shop_site_url, 'contact.html')

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
                headers = {
                    'referer': shop_site_url
                }
                next_request = Request(about_url, headers=headers, callback=self.parse_about_page)
            item = LegItem(collection=self.collection, doc=doc,
                           next_request=next_request, list_url=list_url, query=query)
            yield self.item_or_request(item)

    def parse_about_page(self, response):
        item = response.meta['item']
        doc = item['doc']
        html5_response = response_html5parse(response)
        page_hxs = HtmlXPathSelector(html5_response)

        shop_products_hxs = page_hxs.select('//div[@class="box770"]//div[@class="Wireframe"]//text()')
        shop_products = parse_products(shop_products_hxs)

        shop_launch_time = ''.join(page_hxs.select('/html/body/div[9]/div[2]/div[3]/div[2]/div[2]/p[2]/span[1]//text()').extract())
        shop_launch_time = shop_launch_time.strip()

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

        contact_hxs = page_hxs.select('//div[@class="contact"]//text()')
        contact_dic = parse_contact(contact_hxs)

        shop_contacts = ''.join(page_hxs.select('/html/body/div[9]/div[2]/div/div[2]/strong[2]//text()').extract())
        shop_contacts = shop_contacts.strip()

        doc.update(contact_dic)
        if shop_contacts:
            doc['shop_contacts'] = shop_contacts

        yield self.item_or_request(item)

    def process_item(self, item):
        process_company_item(item, self)

    def save_item(self, item):
        save_company_item(item)