#coding=utf8
#!/usr/bin/env python
"""


中国供应商 商家信息
cmd:
scrapy crawl zhongguogongyingshang_company_spider --logfile=/tmp/zhongguogongyingshang_company.txt
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


class zhongguogongyingshangCompanySpider(LegSpider):
    name = 'zhongguogongyingshang_company_spider'
    querys = ['淄博']
    entry_url = 'http://product.cn.china.cn/suppliers/'
    #搜索不可用
    #search_form_order = 0
    #search_input_name = 'sk'
    #翻页可用
    next_page_word = '下一页'

    visit_detail = True
    #db
    collection = 'shop_info'
    #shop
    shop_site_type = '中国供应商'
    #validate
    item_doc_length = 24
    #spider_kwargs

    def __init__(self, *args, **kwargs):
        super(zhongguogongyingshangCompanySpider, self).__init__(*args, **kwargs)

    def init(self):
        return self._detect_site_default_encoding()

    def get_entry_request(self, query):
        url = os.path.join(self.entry_url.encode(self._site_default_encoding), query.encode(self._site_default_encoding))
        headers = {
            'referer': 'http://product.cn.china.cn/industry/',
        }
        meta = {
            'query': query,
            'page_num': 0,
        }
        request = Request(url=url, headers=headers, callback=self.query_callback, meta=meta)
        return request

    def parse_list_page(self, response):
        """
        """
        multi_xpath = '//li[@class="sr-lst"]'
        html5_response = response_html5parse(response)
        page_hxs = HtmlXPathSelector(html5_response)
        multi_hxs = page_hxs.select(multi_xpath)
        for hxs in multi_hxs:
            shop_name = ''.join(hxs.select('./div/h2/a//text()').extract())
            shop_name = clean_string(shop_name)
            shop_site_url = ''.join(hxs.select('./div/h2/a/@href').extract())
            shop_site_url = urllib.unquote(shop_site_url).strip()
            about_url = os.path.join(shop_site_url, 'company-information')
            contact_url = os.path.join(shop_site_url, 'contact-information')

            doc = {
                'shop_name': shop_name.strip(),
                'shop_site_url': shop_site_url.strip(),
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

        shop_products_hxs = page_hxs.select('//div[@class="box"]//text()')
        shop_products = parse_products(shop_products_hxs)

        shop_launch_time = ''.join(page_hxs.select('//table[@class="com_moreinfo divcolor"]/tbody/tr[5]/td[2]//text()').extract())
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

        contact_hxs = page_hxs.select('//div[@id="rpart"]//tr//text()')
        contact_hxs1 = page_hxs.select('//div[@class="contact-way"]//text()')
        contact_hxs.extend(contact_hxs1)
        contact_dic = parse_contact(contact_hxs)

        doc.update(contact_dic)

        yield self.item_or_request(item)

    def process_item(self, item):
        process_company_item(item, self)

    def save_item(self, item):
        save_company_item(item)