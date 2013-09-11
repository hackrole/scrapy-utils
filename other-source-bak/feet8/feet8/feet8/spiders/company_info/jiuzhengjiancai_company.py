#coding=utf8
#!/usr/bin/env python
"""
九正建材 商家信息
cmd:
scrapy crawl jiuzhengjiancai_company_spider --logfile=/tmp/jiuzhengjiancai_company.txt
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type

#Author:wuya @ smallteam
#Date: 13-5-17

import urllib

from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from feet8.items import LegItem
from feet8.cells.leg_spider import LegSpider
from feet8.utils.misc import response_html5parse, get_url_query, change_url_query
from feet8.utils import fnvhash

from .spider_utils import save_company_item, process_company_item, clean_string, parse_qq_num, parse_products, parse_contact2


class jiuzhengjiancaiCompanySpider(LegSpider):
    name = 'jiuzhengjiancai_company_spider'
    querys = ['淄博']
    entry_url = 'http://shop.jc001.cn'
    search_form_order = 0
    search_input_name = 'sk'
    next_page_word = '下一页'

    visit_detail = True
    #db
    collection = 'shop_info'
    #shop
    shop_site_type = '九正建材'
    #validate
    item_doc_length = 24

    # noinspection PyUnresolvedReferences
    def __init__(self, *args, **kwargs):
        super(jiuzhengjiancaiCompanySpider, self).__init__(*args, **kwargs)

    def get_query_request(self, response):
        request = super(jiuzhengjiancaiCompanySpider, self).get_query_request(response)
        url = request.url
        url = url.replace('goods.jc001.cn', 'shop.jc001.cn')
        request = request.replace(url=url)
        return request

    def get_next_page_request(self, response):
        request = super(jiuzhengjiancaiCompanySpider, self).get_next_page_request(response)
        url = request.url
        query = get_url_query(url)
        p = query.get('p', 1)
        p = int(p)
        query['p'] = str(p + 1)
        url = change_url_query(url, query)
        request = request.replace(url=url)
        return request

    def parse_list_page(self, response):
        multi_xpath = '//div[@class="shopListCon"]//tr'
        html5_response = response_html5parse(response)
        page_hxs = HtmlXPathSelector(html5_response)
        multi_hxs = page_hxs.select(multi_xpath)
        for hxs in multi_hxs:
            shop_name = ''.join(hxs.select('./td[2]//a//text()').extract())
            shop_name = clean_string(shop_name)
            shop_site_url = ''.join(hxs.select('./td[2]//a/@href').extract())
            shop_site_url = urllib.unquote(shop_site_url).strip()

            doc = {
                'shop_name': shop_name,
                'shop_site_url': shop_site_url,
            }

            detail_url = shop_site_url
            query = response.meta['query']
            list_url = response.url
            if not shop_site_url:
                next_request = None
            else:
                next_request = Request(detail_url, callback=self.parse_detail_page)
            item = LegItem(collection=self.collection, doc=doc,
                           next_request=next_request, list_url=list_url, query=query)
            yield self.item_or_request(item)

    def parse_detail_page(self, response):
        item = response.meta['item']
        doc = item['doc']
        html5_response = response_html5parse(response)
        page_hxs = HtmlXPathSelector(html5_response)

        shop_products_hxs = page_hxs.select('//div[@id="about"]//text()')
        shop_products = parse_products(shop_products_hxs, junks=['更多'])

        shop_launch_time = ''.join(page_hxs.select('//div[@id="about"]/div[2]/table/tbody/tr[2]/td[2]//text()').extract())
        shop_launch_time = shop_launch_time.strip()

        contact2_hxs = page_hxs.select('//div[@id="contact"]//table//td//text()')
        contact_dic = parse_contact2(contact2_hxs)

        shop_email = ''.join(page_hxs.select('//div[@id="contact"]/div[2]/table/tbody/tr[8]/td[2]/a/@href').extract())
        shop_email = shop_email.strip().lstrip('mailto:：')

        qq_hxs = page_hxs.select('//div[@id="contact"]')
        shop_qq = parse_qq_num(qq_hxs)

        doc.update(contact_dic)
        doc['shop_products'] = shop_products
        doc['shop_launch_time'] = shop_launch_time
        doc['shop_email'] = shop_email
        doc['shop_qq'] = shop_qq

        yield self.item_or_request(item)

    def process_item(self, item):
        process_company_item(item, self)

    def save_item(self, item):
        save_company_item(item)
