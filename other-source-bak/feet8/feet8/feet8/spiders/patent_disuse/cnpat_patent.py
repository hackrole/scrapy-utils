#coding=utf8
#!/usr/bin/env python
"""
我太菜比,这个站的查询我模拟出来,总是返回给我随机结果-.-
放弃
cnpat_patent爬虫
cmd:
scrapy crawl cnpat_patent --logfile=/tmp/cnpat_patent.txt
scrapy crawl_ex cnpat_patent --logfile=/tmp/cnpat_patent.txt
"""
from __future__ import division, print_function, unicode_literals
import json
import requests
from scrapy import log
import time
from urlparse2 import urlparse, urlunparse
from feet8.pipelines.attachment import get_image_urls

from feet8.spiders.patent.utils import PatentMongodbAdapter, PatentItem
from feet8.utils.multi_convert import response_requests2scrapy,request_scrapy2curl_cmd
from feet8.utils import cookie as cookie_utils

__metaclass__ = type

#Author:wuya @ smallteam
#Date: 13-7-1
import urllib

from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from feet8.cells.leg_spider import LegSpider
from feet8.utils.misc import response_html5parse,  get_mime_type_in_response, get_url_query, change_url_query
#todo temp
from feet8.querys import querys1

class CnpatPatentSpider(LegSpider):
    name = 'cnpat_patent'

    querys = querys1
    querys = ['你好',]

    entry_url = 'http://searchtel.patentstar.com.cn/cprs2010/'
    search_form_order = 0
    search_input_name = 'searchContent'
    next_page_word = '下一页'
    visit_detail = True

    #spider kwargs
    page_count_limit = 0

    #spider_settings
    custom_settings = {
        # 'DOWNLOAD_DELAY': 0,
    }
    #db_adapter
    db_adapter_cls = PatentMongodbAdapter
    _site_default_encoding = 'utf8'

    def get_query_request(self, response):
        query = response.meta['query']
        default_encoding = self._site_default_encoding
        encoding = default_encoding if default_encoding else response.encoding
        query = query.encode(encoding)
        _kw = urllib.quote(query,safe=b':=&()?')
        _query = urllib.quote(b" (%(query)s/AB+%(query)s/CL+%(query)s/TI+%(query)s/IN+%(query)s/PA)" % {'query':query},safe=b'()')
        # referer = b'http://searchtel.patentstar.com.cn/CPRS2010/cn/PatentGeneralList.html?No=999&kw=%s&Query=%s'%(_kw,_query)
        referer = b'http://searchtel.patentstar.com.cn/CPRS2010/cn/PatentGeneralList.html?No=999&kw=%s&Nm=23&errorTips=&Query=%s'%(_kw,_query)
        # _kw = query
        # _query = b" (%(query)s/AB+%(query)s/CL+%(query)s/TI+%(query)s/IN+%(query)s/PA)" % {'query':query}
        # referer = b'http://searchtel.patentstar.com.cn/CPRS2010/cn/PatentGeneralList.html?No=999&kw=%s&Nm=23&errorTips=&Query=%s'%(_kw,_query)
        # url_query = get_url_query(referer)
        # for k,v in url_query.items():
        #     url_query[k] = urllib.quote(v,safe=b':=&()?')
        # new_query = ''
        # new_query = '&'.join('%s=%s'%(k,v) for k,v in url_query.items())
        # up_result = urlparse(referer)
        # up_result.query = new_query
        # referer = urlunparse(up_result)
        # referer = change_url_query(referer,url_query)
        # referer = urllib.quote(referer,safe=b':/=&()?')
        headers = {
            'Accept':'application/json, text/javascript, */*',
            'Content-Type': 'application/json; charset=UTF-8',
            'Referer': referer,
            # 'Cookie': get_cookie(),
            'X-Requested-With':'XMLHttpRequest',
        }
        data=b"{'PageSize':'10', 'PageNumber':'1','_strSearchNo':'999'}"
        url = 'http://searchtel.patentstar.com.cn/CPRS2010/cn/PatentGeneralList.aspx/GetXmlResult'
        # url = 'http://searchtel.patentstar.com.cn/CPRS2010/cn/PatentGeneralList.aspx/GetXmlResult'
        request = Request(url,method='POST',headers=headers,body=data)
        # noinspection PyUnresolvedReferences
        request.callback = self.query_callback
        return request

    def get_next_page_request(self, response):
        sleep_time = self.crawler.settings.get('DOWNLOAD_DELAY',1)
        time.sleep(sleep_time)
        request_data = response.request.body
        data = json.loads(request_data)
        page_number = data.get('PageNumber',None)
        if not page_number:
            return
        page_number = int(page_number) + 1
        data['PageNumber'] = page_number
        referer = response.request.headers['Referer']
        url = 'http://searchtel.patentstar.com.cn/CPRS2010/cn/PatentGeneralList.aspx/GetXmlResult'
        # url = 'http://searchtel.patentstar.com.cn/CPRS2010/cn/PatentGeneralList.aspx/GetXmlResult'
        headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            'Referer': referer,
            'Cookie': get_cookie(),
        }
        _response = requests.post(url, data=json.dumps(data),headers=headers)
        try:
            result = _response.json()
            if result['d'][0] is not None:
                immediate_response = response_requests2scrapy(_response)
                meta = {
                    'immediate_response': immediate_response
                }
                request = Request(url,headers=headers,method='POST',meta=meta)
                # noinspection PyUnresolvedReferences
                request.callback = self.query_callback
                return request
        except Exception as e:
            log.msg('spider turn page error:%s' % str(e), level=log.INFO)
            return None

    def parse_list_page(self, response):
        try:
            result = json.loads(response.body_as_unicode())
        except Exception as e:
            log.msg('parse_list_page error:%s' % e)
            return
        if result is None:
            result = []
        for dic in result:
            cic = dic.get('CPIC','')
            # noinspection PyShadowingBuiltins
            id = dic.get('StrApNo','')
            idk = dic.get('StrANX','')
            url = 'http://searchtel.patentstar.com.cn/CPRS2010/cn/PatentDetails.html?cic=%s&id=%s&idk=%s' % (cic,id,idk)
            doc = {
                'data_source': '专利之星中国专利搜索',
                'url':url,
                'applicant_address': dic.get('Address',''),
                'abstract': dic.get('StrAbstr',''),
                # '':dic.get('StrAgency',''),
                'agent_person':dic.get('StrAgent',''),
                'application_time': dic.get('StrApDate',''),
                'application_number': dic.get('StrApNo',''),
                'applicant': dic.get('StrApply',''),
                'claims': dic.get('StrClaim', ''),
                'inventor': dic.get('StrInventor', ''),
                'classification': dic.get('StrIpc', ''),
                'publication_number': dic.get('StrPubNo','').strip('公开号：'),
                'publication_time': dic.get('StrPubDate','').strip('公开日：'),
                'patent_name': dic.get('StrTitle', ''),
                #---
                'dic':dic,
            }
            detail_url = ''
            if cic and id and idk:
                detail_url = url
            list_url = response.url
            query = response.meta.get('query')
            if not detail_url:
                next_request = None
            else:
                next_request = Request(detail_url, callback=self.parse_detail_page)
            item = PatentItem(doc=doc,
                              next_request=next_request, list_url=list_url, query=query,
                              attachments=[], attachment_urls=[])
            yield self.item_or_request(item)

    def parse_detail_page(self, response):
        item = response.meta['item']

        html5_response = response_html5parse(response)
        hxs = HtmlXPathSelector(html5_response)

        abstract = ''.join(hxs.select('//span[@id="txtAbstr"]//text()').extract())
        agent_institution = ''.join(hxs.select('//span[@id="tdANM"]//text()').extract())
        claims = ''.join(hxs.select('//span[@id="txtClaim"]//text()').extract())

        doc = item['doc']
        doc['abstract'] = abstract
        doc['agent_institution'] = agent_institution
        doc['claims'] = claims

        dic = doc['dic']
        pno = 'APP%s'%dic['StrANX']
        pdf_url = 'http://searchtel.patentstar.com.cn/CPRS2010/Docdb/GetBns.aspx?PNo=%s'%pno
        next_request = Request(pdf_url,callback=self.parse_pdf)
        item['next_request'] = next_request

        attachments = item['attachments']
        attach1 = {
            'url': response.url,
            'data': response.body_as_unicode(),
            'mime_type': get_mime_type_in_response(response)
        }
        attachments.append(attach1)
        yield self.item_or_request(item)

    def parse_pdf(self, response):
        item = response.meta['item']
        html5_response = response_html5parse(response)
        hxs = HtmlXPathSelector(html5_response)
        pdf_url = ''.join(hxs.select('//a[text()="公开文本"]/@href'))
        if pdf_url:
            item['attachment_urls'].append(pdf_url)
        doc = item['doc']
        dic = doc['dic']
        idx = dic['StrANX']
        images_url = 'http://searchtel.patentstar.com.cn/CPRS2010/comm/getzhaiyao.aspx?idx=%s'%idx
        next_request = Request(images_url,callback=self.parse_images)
        item['next_request'] = next_request
        yield self.item_or_request(item)

    def parse_images(self, response):
        item = response.meta['item']
        image_urls = get_image_urls(response)
        item['attachment_urls'] += image_urls
        yield self.item_or_request(item)


import Queue
_cookies = Queue.Queue()
def get_cookie():
    global _cookies
    if _cookies.empty():
        url = 'http://searchtel.patentstar.com.cn/CPRS2010/'
        headers = {}
        cookies_list = []
        # for x in xrange(10):
        #todo temp
        for x in xrange(1):
            response = requests.get(url, headers=headers)
            cookies = response.cookies.get_dict()
            cookies = cookie_utils.dict2str(cookies)
            cookies_list.extend([cookies] * 100)
        while len(cookies_list):
            _cookies.put(cookies_list.pop())
        return get_cookie()
    else:
        return _cookies.get()
