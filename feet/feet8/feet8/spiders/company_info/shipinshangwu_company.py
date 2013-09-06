#coding=utf8
#!/usr/bin/env python
"""


食品商务 商家信息
cmd:
scrapy crawl shipinshangwu_company_spider --logfile=/tmp/shipinshangwu_company.txt
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

from .spider_utils import save_company_item, parse_qq_num, clean_string, parse_products, parse_contact2, process_company_item


class shipinshangwuCompanySpider(LegSpider):
    name = 'shipinshangwu_company_spider'
    querys = ['淄博']
    entry_url = 'http://www.21food.cn/company/'
    search_form_order = 1
    search_input_name = 'keys'
    next_page_word = '下一页'

    visit_detail = True
    #db
    collection = 'shop_info'
    #shop
    shop_site_type = '食品商务'
    #validate
    item_doc_length = 24
    #spider_kwargs

    def __init__(self, *args, **kwargs):
        super(shipinshangwuCompanySpider, self).__init__(*args, **kwargs)

    def parse_list_page(self, response):
        multi_xpath = '//div[@class="supply-cell" or @class="supply-cell supply-cell-bg"]'
        html5_response = response_html5parse(response)
        page_hxs = HtmlXPathSelector(html5_response)
        multi_hxs = page_hxs.select(multi_xpath)
        for hxs in multi_hxs:
            shop_name = ''.join(hxs.select('./div/div/span/a//text()').extract())
            shop_name = clean_string(shop_name)
            shop_site_url = ''.join(hxs.select('./div/div/span/a[1]/@href').extract())
            shop_site_url = urllib.unquote(shop_site_url).strip()

            detail_url = shop_site_url

            doc = {
                'shop_name': shop_name,
                'shop_site_url': shop_site_url,
            }

            query = response.meta['query']
            list_url = response.url

            if not shop_site_url:
                next_request = None
            else:
                headers = {
                    'referer': shop_site_url
                }
                next_request = Request(detail_url, headers=headers, callback=self.parse_about_page)
            item = LegItem(collection=self.collection, doc=doc,
                           next_request=next_request, list_url=list_url, query=query)
            yield self.item_or_request(item)

    def parse_detail_page(self, response):
        item = response.meta['item']
        doc = item['doc']
        html5_response = response_html5parse(response)
        page_hxs = HtmlXPathSelector(html5_response)

        shop_site_url = doc.get('shop_site_url', '')

        about_url = ''.join(page_hxs.select('//a[text()="公司介绍"]/@href').extract()[0]).lstrip('/')
        contact_url = ''.join(page_hxs.select('//a[text()="联系方式"]/@href').extract()[0]).lstrip('/')
        about_url = os.path.join(shop_site_url, about_url)
        contact_url = os.path.join(shop_site_url, contact_url)

        doc['about_url'] = about_url
        doc['contact_url'] = contact_url

        if not shop_site_url:
            next_request = None
        else:
            next_request = Request(about_url, callback=self.parse_about_page)
        item['next_request'] = next_request
        yield self.item_or_request(item)

    def parse_about_page(self, response):
        item = response.meta['item']
        doc = item['doc']
        html5_response = response_html5parse(response)
        page_hxs = HtmlXPathSelector(html5_response)

        shop_products_hxs = page_hxs.select('//div[@id="rightPlate"]//text()')
        shop_products_hxs1 = page_hxs.select('/html/body/table[6]/tbody/tr/td[2]/table[2]//text()')
        shop_products_hxs.extend(shop_products_hxs1)
        shop_products = parse_products(shop_products_hxs)

        shop_launch_time = ''.join(page_hxs.select('//div[@id="rightPlate"]/div/div[2]/div[2]/table/tbody/tr[2]/td[2]//text()').extract())

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

        contact2_hxs = page_hxs.select('//div[@class="contact"][1]//div//text()')
        contact2_dic = parse_contact2(contact2_hxs)

        qq_hxs = page_hxs.select('//div[@class="contact"][1]')
        shop_qq = parse_qq_num(qq_hxs)

        doc.update(contact2_dic)
        doc['shop_qq'] = shop_qq

        yield self.item_or_request(item)

    def process_item(self, item):
        process_company_item(item, self)

    def save_item(self, item):
        save_company_item(item)
