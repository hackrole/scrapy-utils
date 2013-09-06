#coding=utf8
#!/usr/bin/env python
"""


中国建材 商家信息
cmd:
scrapy crawl zhongguojiancai_company_spider --logfile=/tmp/zhongguojiancai_company.txt
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

from .spider_utils import clean_string, parse_products, parse_contact, parse_qq_num, process_company_item, save_company_item


class zhongguojiancaiCompanySpider(LegSpider):
    name = 'zhongguojiancai_company_spider'
    querys = ['淄博']
    entry_url = 'http://www.bmlink.com/company/'
    search_form_order = 0
    search_input_name = 'key'
    next_page_word = '下一页'

    visit_detail = True
    #db
    collection = 'shop_info'
    #shop
    shop_site_type = '中国建材'
    #validate
    item_doc_length = 24
    #spider_kwargs

    def __init__(self, *args, **kwargs):
        super(zhongguojiancaiCompanySpider, self).__init__(*args, **kwargs)

    def parse_list_page(self, response):
        """
        """
        multi_xpath = '//div[@class="border_b list_tiao"]'
        html5_response = response_html5parse(response)
        page_hxs = HtmlXPathSelector(html5_response)
        multi_hxs = page_hxs.select(multi_xpath)
        for hxs in multi_hxs:
            shop_name = ''.join(hxs.select('.//div[@class="c_name"]/a//text()').extract())
            shop_name = clean_string(shop_name)
            shop_site_url = ''.join(hxs.select('.//div[@class="c_name"]/a/@href').extract())
            shop_site_url = urllib.unquote(shop_site_url).strip()
            about_url = os.path.join(shop_site_url, 'company')
            contact_url = os.path.join(shop_site_url, 'contact')

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

        shop_products_hxs = page_hxs.select('//div[@id="b740"]//text()')
        shop_products = parse_products(shop_products_hxs)
        shop_launch_time = ''.join(page_hxs.select('//div[@id="b740"]/div[2]/table[2]/tbody/tr[1]/td[2]//text()').extract())
        shop_launch_time = shop_launch_time.strip()

        doc['shop_products'] = shop_products.strip()
        doc['shop_launch_time'] = shop_launch_time.strip()

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

        contact_hxs = page_hxs.select('//div[@id="b740"]/div/dl//text()')
        contact_dic = parse_contact(contact_hxs)

        qq_hxs = page_hxs.select('//div[@id="b740"]')
        shop_qq = parse_qq_num(qq_hxs)

        doc.update(contact_dic)
        doc['shop_qq'] = shop_qq

        yield self.item_or_request(item)

    def process_item(self, item):
        process_company_item(item, self)

    def save_item(self, item):
        save_company_item(item)