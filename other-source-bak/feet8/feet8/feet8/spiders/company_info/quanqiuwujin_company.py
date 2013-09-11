#coding=utf8
#!/usr/bin/env python
"""


全球五金 商家信息
cmd:
scrapy crawl quanqiuwujin_company_spider --logfile=/tmp/quanqiuwujin_company.txt
oop

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
from feet8.utils.misc import response_html5parse
from feet8.utils import fnvhash

from .spider_utils import save_company_item, parse_products, parse_contact1, process_company_item, parse_qq_num, clean_string


class quanqiuwujinCompanySpider(LegSpider):
    name = 'quanqiuwujin_company_spider'
    querys = ['淄博']
    entry_url = 'http://sou.wjw.cn/qiye/'
    #搜索不可用
    #search_form_order = 0
    #search_input_name = 'sk'
    #翻页不可用
    #next_page_word = '下一页'

    visit_detail = True
    #db
    collection = 'shop_info'
    #shop
    shop_site_type = '全球五金'
    #validate
    item_doc_length = 24

    def __init__(self, *args, **kwargs):
        super(quanqiuwujinCompanySpider, self).__init__(*args, **kwargs)

    def init(self):
        return self._detect_site_default_encoding()

    def get_entry_request(self, query):
        url = ('http://sou.wjw.cn/qiye/_%s__________.xhtml' % query).encode(self._site_default_encoding)
        headers = {
            'referer': 'http://sou.wjw.cn/qiye/',
        }
        meta = {
            'query': query,
            'page_num': 0,
        }
        request = Request(url=url, headers=headers, callback=self.query_callback, meta=meta)
        return request

    def get_next_page_link(self):
        def predicate(link):
            attrs_dic = dict(link.attrs)
            if attrs_dic.get('class') == 'nxtpage':
                return True
        link = self.br.find_link(predicate=predicate)
        return link

    def parse_list_page(self, response):
        multi_xpath = '//div[@class="jieguo"]'
        html5_response = response_html5parse(response)
        page_hxs = HtmlXPathSelector(html5_response)
        multi_hxs = page_hxs.select(multi_xpath)
        for hxs in multi_hxs:
            shop_name = ''.join(hxs.select('./div[2]/ul/li[1]/a//text()').extract())
            shop_name = clean_string(shop_name)
            shop_site_url = ''.join(hxs.select('./div[2]/ul/li[1]/a/@href').extract())
            shop_site_url = urllib.unquote(shop_site_url).strip()
            _shop_id = shop_site_url.split('/')[4]
            about_url = 'http://www.wjw.cn/companyprofile/%s/aboutus.xhtml' % _shop_id
            contact_url = 'http://www.wjw.cn/cardview/%s/card.xhtml' % _shop_id

            doc = {
                'shop_name': shop_name,
                'shop_site_url': shop_site_url,
                'about_url': about_url,
                'contact_url': contact_url,
            }

            query = response.meta['query']
            list_url = response.url

            if not _shop_id:
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

        shop_products_hxs = page_hxs.select('//div[@class="MainRightBox1"]//text()')
        shop_products = parse_products(shop_products_hxs, junks=['证书荣誉'])
        shop_launch_time = ''.join(page_hxs.select('//table[@id="ctl00_ShopBody_tabZizhi"]/tbody/tr[3]/td[2]//text()').extract())
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

        contact1_hxs = page_hxs.select('//div[@class="MpBox MpBoxBg"]//p//text()')
        contact1_dic = parse_contact1(contact1_hxs)

        shop_contacts = ''.join(page_hxs.select('//div[@class="MpBox MpBoxBg"]/p[1]//text()').extract())
        shop_contacts = clean_string(shop_contacts)
        qq_hxs = page_hxs.select('//div[@class="MainLeftBox1"]')
        shop_qq = parse_qq_num(qq_hxs)

        doc.update(contact1_dic)
        doc['shop_contacts'] = shop_contacts
        doc['shop_qq'] = shop_qq

        yield self.item_or_request(item)

    def process_item(self, item):
        process_company_item(item, self)

    def save_item(self, item):
        save_company_item(item)
