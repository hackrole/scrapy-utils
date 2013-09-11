#coding=utf8
#!/usr/bin/env python
#todo here i am
"""


中国制造 商家信息
cmd:
scrapy crawl zhongguozhizao_company_spider --logfile=/tmp/zhongguozhizao_company.txt
oop

"""

from __future__ import division, print_function, unicode_literals
from mechanize import LinkNotFoundError

from feet8.utils.multi_convert import response_scrapy2mechanize

__metaclass__ = type

#Author:wuya @ smallteam
#Date: 13-5-17
import os
import urllib

from scrapy.selector import HtmlXPathSelector
from scrapy import log
from scrapy.http import Request

from feet8.items import LegItem
from feet8.cells.leg_spider import LegSpider
from feet8.utils.misc import response_html5parse, get_url_query, change_url_query
from feet8.utils import fnvhash

from .spider_utils import clean_string, parse_products, parse_contact, process_company_item, save_company_item


class zhongguozhizaoCompanySpider(LegSpider):
    name = 'zhongguozhizao_company_spider'
    querys = ['淄博']
    entry_url = 'http://cn.made-in-china.com/'
    search_form_order = 0
    search_input_name = 'word'
    #翻页不可用
    #next_page_word = '下一页'

    visit_detail = True
    #db
    collection = 'shop_info'
    #shop
    shop_site_type = '中国制造'
    #validate
    item_doc_length = 24
    #spider_kwargs


    # noinspection PyUnresolvedReferences
    def __init__(self, *args, **kwargs):
        super(zhongguozhizaoCompanySpider, self).__init__(*args, **kwargs)

    def init(self):
        self._detect_site_default_encoding()

    def get_query_request(self, response):
        request = super(zhongguozhizaoCompanySpider, self).get_query_request(response)
        new_url = request.url.replace('productdirectory.do', 'companysearch.do')
        request = request.replace(url=new_url)
        return request

    def get_next_page_request(self, response):
        br = self.br
        mechanize_response = response_scrapy2mechanize(response)
        br.set_response(mechanize_response)
        encoding = response.encoding
        next_page_word = self.next_page_word.encode(encoding)
        next_page_link = self.get_next_page_link()
        try:
            if next_page_link:
                next_page_request = br.click_link(link=next_page_link)
            else:
                next_page_request = br.click_link(text=next_page_word)
            if next_page_request:
                url = response.url
                query = get_url_query(url)
                page = str(int(query.get('page', '1')) + 1)
                query['page'] = page
                url = change_url_query(url, query)
                scrapy_request = Request(url=url, callback=self.query_callback)
                return scrapy_request
            else:
                return None
        except LinkNotFoundError as e:
            return None
        except Exception as e:
            self.log('spider turn page error:%s' % e, level=log.INFO)
            return None

    def parse_list_page(self, response):
        """
        """
        multi_xpath = '//div[@class="prolist" or @class="prolist prolistO"]'
        html5_response = response_html5parse(response)
        page_hxs = HtmlXPathSelector(html5_response)
        multi_hxs = page_hxs.select(multi_xpath)
        for hxs in multi_hxs:
            shop_name = ''.join(hxs.select('.//div[@class="cntC"]/p[1]//a//text()').extract())
            shop_name = clean_string(shop_name)
            shop_site_url = ''.join(hxs.select('.//div[@class="cntC"]/p[1]//a/@href').extract())
            shop_site_url = urllib.unquote(shop_site_url).strip()
            detail_url = shop_site_url

            doc = {
                'shop_name': shop_name.strip(),
                'shop_site_url': shop_site_url.strip(),
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

        shop_site_url = doc.get('shop_site_url', '')

        about_url = ''.join(page_hxs.select('//a[./span/text()="公司信息"]/@href').extract()[0]).lstrip('/')
        contact_url = ''.join(page_hxs.select('//a[./span/text()="联系方式"]/@href').extract()[0]).lstrip('/')
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

        shop_products_hxs = page_hxs.select('//div[@class="side_2"]//text()')
        junks = [
            '加入失败',
            '您的询盘篮内信息已满0条！',
            '达到信息添加上限',
            '加入成功',
            '已成功添加到询盘篮！',
            '您的询盘篮中共有0家公司的0个产品',
            '继续浏览',
        ]
        shop_products = parse_products(shop_products_hxs, junks=junks)

        doc['shop_products'] = shop_products.strip()

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

        contact_hxs = page_hxs.select('//table//tr//text()')
        contact_dic = parse_contact(contact_hxs)

        shop_contacts = ''.join(page_hxs.select('//div[@class="card-detail"]/h3/a//text()').extract())
        shop_contacts = shop_contacts.strip()

        doc['shop_contacts'] = shop_contacts
        doc.update(contact_dic)
        yield self.item_or_request(item)

    def process_item(self, item):
        process_company_item(item, self)

    def save_item(self, item):
        save_company_item(item)
