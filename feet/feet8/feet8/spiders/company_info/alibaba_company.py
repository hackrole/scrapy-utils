#coding=utf8
#!/usr/bin/env python
#todo,low 有屏蔽
"""
有屏蔽:
只能翻一页...你懂得-.-不是频率限制


alibaba商家信息爬虫
cmd:
scrapy crawl alibaba_company_spider --logfile=/tmp/alibaba_company.txt
"""
from __future__ import division, print_function, unicode_literals
from feet8.spiders.company_info.spider_utils import calc_shop_owner_type

__metaclass__ = type

#Author:wuya @ smallteam
#Date: 13-5-17

import urllib
import datetime

from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from feet8.items import LegItem
from feet8.cells.leg_spider import LegSpider
from feet8.utils.misc import response_html5parse, get_url_query, change_url_query, get_site_url

# noinspection PyUnresolvedReferences
from feet8.utils import fnvhash



class AlibabaCompanySpider(LegSpider):
    name = 'alibaba_company_spider'
    querys = ['淄博']
    entry_url = 'http://search.china.alibaba.com/company/company_search.htm'
    search_form_order = 0
    search_input_name = 'keywords'
    next_page_word = '下一页'

    visit_detail = False
    #db
    collection = 'shop_info'
    #shop
    shop_site_type = '阿里巴巴cbu'
    #spider_kwargs
    province = '山东'
    city = '淄博'
    page_count_limit = 200

    # noinspection PyUnresolvedReferences
    def __init__(self, *args, **kwargs):
        """
        province = ''
        city = ''
        """
        super(AlibabaCompanySpider, self).__init__(*args, **kwargs)

    def get_query_request(self, response):
        """
        填表单,构造相应请求
        """
        request = super(AlibabaCompanySpider, self).get_query_request(response)
        encoding = response.encoding
        url = request.url
        query = get_url_query(url)
        query['province'] = self.province.encode(encoding)
        query['city'] = self.city.encode(encoding)
        query['filt'] = b'y'
        query.pop('button_click', None)
        new_url = change_url_query(url, query)
        request = request.replace(url=new_url)
        return request

    def parse_list_page(self, response):
        """
        商店名:抓取
        性质:计算
        来源:计算
        类别:抓取?
        店主:抓取
        地址:抓取
        联系方式:抓取
        创店日期:抓取
        主营产品:抓取
        状态:?
        操作:不需要
        shop_info = {}
        shop_info['shop_type_id'] = 10
        shop_info['shop_name'] = self.company
        shop_info['shop_address'] = self.address
        if not self.address:
            shop_info['shop_address'] = '山东淄博'
        shop_info['shop_contacts'] = self.contact
        shop_info['shop_phone'] = self.phone
        shop_info['shop_products'] = self.keywords
        shop_info['shop_site_url'] = self.site_url
        shop_info['shop_site_url_hash'] = fnvhash.fnv_64a_str(self.site_url)
        shop_info['shop_site_type'] = 24
        shop_info['shop_certified'] = 1
        shop_info['shop_owner_type'] = 1
        company_key = ['厂','站','公司', '事务所', '集团']
        for item in company_key:
            if item in self.company:
                shop_info['shop_owner_type'] = 2
        """


        multi_xpath = '//*[@id="sw_mod_searchlist"]/ul/li'
        html5_response = response_html5parse(response)
        page_hxs = HtmlXPathSelector(html5_response)
        multi_hxs = page_hxs.select(multi_xpath)
        for hxs in multi_hxs:
            #shop_products为shop相关所有描述.包括主营产品,简要描述和细节描述
            #提取部分
            shop_name = ''.join(hxs.select('.//a[@class="sw-ui-font-title14"]//text()').extract())
            shop_address = ''.join(hxs.select('.//div[@class="sm-offerResult-address"]/a/text()').extract())
            #主营产品： 有机化工原料; 苯 醇 酯 醚 类 批发
            #这是部分主营产品,所有主营产品在主营产品 链接里的标题里面
            shop_part_products = ''.join(hxs.select('.//div[@class="sm-offerResult-sale"]//text()').extract())
            shop_brief = ''.join(hxs.select('.//div[@class="sm-offerResult-sub"]//text()').extract())
            creditdetail_url = ''.join(hxs.select('.//a[@class="sw-ui-font-title14"]/@href').extract())
            creditdetail_url = urllib.unquote(creditdetail_url).strip()
            #计算部分
            shop_products = shop_brief + shop_part_products
            creditdetail_url_query = get_url_query(creditdetail_url)
            creditdetail_url_query.pop('tracelog', None)
            creditdetail_url = change_url_query(creditdetail_url, creditdetail_url_query)
            shop_site_url = get_site_url(creditdetail_url)
            shop_owner_type = calc_shop_owner_type(shop_name)
            shop_site_url_hash = fnvhash.fnv_64a_str(shop_site_url)
            #无对应数据部分
            shop_qq = None
            shop_email = None
            lack_doc = {
                'shop_qq': shop_qq,
                'shop_email': shop_email,
            }
            #默认填充部分
            shop_type_id = None
            shop_area_id = None
            shop_site_type = self.shop_site_type
            shop_certified = 1
            city_id = 1
            is_bad_url = 0
            is_bad_time = None
            deleted = 0
            isRead = 0
            isImport = 0
            default_doc = {
                'shop_type_id': shop_type_id,
                'shop_area_id': shop_area_id,
                'shop_site_type': shop_site_type,
                'shop_certified': shop_certified,
                'city_id': city_id,
                'is_bad_url': is_bad_url,
                'is_bad_time': is_bad_time,
                'deleted': deleted,
                'isRead': isRead,
                'isImport': isImport,
            }
            now = datetime.datetime.utcnow()

            doc = {
                'shop_name': shop_name,
                'shop_address': shop_address,
                'shop_products': shop_products,
                'shop_site_url': shop_site_url,
                'shop_site_url_hash': shop_site_url_hash,
                'show_owner_type': shop_owner_type,
                'crawl_time': now,
            }
            doc.update(lack_doc)
            doc.update(default_doc)

            detail_url = creditdetail_url
            list_url = response.url
            query = response.meta.get('query')
            item = LegItem(collection=self.collection, doc=doc,
                              detail_url=detail_url, list_url=list_url, query=query)
            if detail_url and self.visit_detail:
                detail_request = Request(detail_url, callback=self.parse_detail_page)
                detail_request.meta['item'] = item
                detail_request.meta['query'] = query
                yield detail_request
            else:
                yield item

    def parse_detail_page(self, response):
        html5_response = response_html5parse(response)
        page_hxs = HtmlXPathSelector(html5_response)
        #提取部分
        shop_lauch_time = ''.join(page_hxs.select('//*[@id="archive-base-info"]/div[2]/div[1]/div[2]/div[2]/ul[1]/li[1]/text()').extract())
        shop_contacts = ''.join(page_hxs.select('//*[@id="memberinfo"]/div[2]/dl/dd[1]/@title').extract())
        shop_cellphone = ''.join(page_hxs.select('//*[@id="memberinfo"]/div[2]/dl/dd[2]/text()').extract())
        shop_phone = ''.join(page_hxs.select('//*[@id="memberinfo"]/div[2]/dl/dd[3]/text()').extract())
        shop_detail = ''.join(page_hxs.select('//div[@id="company-more/text()"]').extract())
        #计算部分
        item = response.meta['item']
        doc = item.get('doc', {})
        shop_products = doc.get('shop_products', '')
        shop_products += shop_detail

        doc['shop_products'] = shop_products
        doc['shop_lauch_time'] = shop_lauch_time
        doc['shop_contacts'] = shop_contacts
        doc['shop_cellphone'] = shop_cellphone
        doc['shop_phone'] = shop_phone

        yield item

#todo
#shop_type_id ?如何?
#shop_area_id ?地区id没找到计算代码
#shop_site_url_hash ?这个库是pypi上的,还是自己弄的,pip install xx?
#shop_site_type 貌似是来源站?如何填
#shop_certified 绝大部分直接1?

#city_id    直接1
#is_bad_url 直接0
#is_bad_time    None

#deleted    0 1?
#isRead     0 1?
#isImport   直接0


#crawl_time done
#shop_site_url_hash fnv_hash wait to be done
#shop_owner_type done