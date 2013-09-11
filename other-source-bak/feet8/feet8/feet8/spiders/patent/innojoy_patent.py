#coding=utf8
#!/usr/bin/env python
"""
innojoy_patent爬虫
cmd:
scrapy crawl innojoy_patent --logfile=/tmp/innojoy_patent.txt
scrapy crawl_ex innojoy_patent --logfile=/tmp/innojoy_patent.txt
"""
from __future__ import division, print_function, unicode_literals
import json

from scrapy import log

from feet8.spiders.patent.utils import PatentMongodbAdapter, PatentItem
from feet8.utils.cleaner import common_clean
from feet8.utils.misc import get_mime_type_in_response

__metaclass__ = type

#Author:wuya @ smallteam
#Date: 13-7-1

from scrapy.http import Request

from feet8.cells.leg_spider import LegSpider

#todo temp
from feet8.querys import querys1


class InnojoyPatentSpider(LegSpider):
    name = 'innojoy_patent'

    querys = querys1
    # querys = ['你好']#,'1',]

    entry_url = 'http://www.innojoy.com/search/index.shtml'
    visit_detail = True

    #db_adapter
    db_adapter_cls = PatentMongodbAdapter

    _page_size = 100
    _query_item_limit = {}

    def _construct_query(self, page_num, query):
        url = 'http://www.innojoy.com/client/interface.aspx'
        data = {"requestModule": "PatentSearch",
                "userId": "",
                "patentSearchConfig": {
                    "Query": query,
                    "TreeQuery": "",
                    "Database": "idpat,mypat,phpat,sgpat,itpat,inpat,inapp,chpat,frpat,gbpat,depat,jpapp,eppat,wopat,usapp,usdes,uspp,usre,uspat,fmsq,wgzl,syxx,fmzl",
                    "Action": "Search",
                    "Page": str(page_num),
                    "PageSize": self._page_size,
                    "GUID": "",
                    "Sortby": "",
                    "AddOnes": "",
                    "DelOnes": "",
                    "RemoveOnes": "",
                    "TrsField": "",
                    "SmartSearch": ""
                }
        }
        data_bin = json.dumps(data)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'http://www.innojoy.com/SearchResult/default.shtml',
        }
        request = Request(url=url, method='post', headers=headers, body=data_bin)
        # noinspection PyUnresolvedReferences
        request.callback = self.query_callback
        return request

    def _construct_full_text(self, dn, db):
        url = 'http://www.innojoy.com/client/interface.aspx'
        headers = {
            #'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'http://www.innojoy.com/SearchResult/default.shtml',
        }
        data = {"requestModule": "PatentSearch",
                "patentSearchConfig": {
                    "Query": "DN=%s" % dn,
                    "Database": db,
                    "PageSize": 1,
                    "RecordIndex": 0,
                    "Action": "loadFullText"
                }
        }
        data_bin = json.dumps(data)
        request = Request(url=url, method='post', headers=headers, body=data_bin)
        # noinspection PyUnresolvedReferences
        request.callback = self.parse_full_text
        return request

    def get_query_request(self, response):
        query = response.meta['query']
        request = self._construct_query(page_num=1, query=query)
        return request

    def get_next_page_request(self, response):
        try:
            query = response.meta['query']
            request_body_json = json.loads(response.request.body)
            last_page_num = int(request_body_json['patentSearchConfig']['Page'])
            query_item_limit = self._query_item_limit[query]
            page_limit = int(query_item_limit / self._page_size) + 1
            if last_page_num + 1 <= page_limit:
                request = self._construct_query(page_num=last_page_num + 1, query=query)
                # noinspection PyUnresolvedReferences
                request.callback = self.query_callback
            else:
                return None
        except Exception as e:
            log.msg('spider turn page error:%s' % str(e), level=log.INFO)
            return None

    def parse_list_page(self, response):
        query = response.meta['query']

        try:
            result = json.loads(response.body_as_unicode())
            if result.get('ErrorInfo', (not None)):
                self._query_item_limit[query] = 0
            else:
                query_item_limit = result['Option']['Count']
                self._query_item_limit[query] = query_item_limit
            patent_list = result['Option']['PatentList']
        except Exception as e:
            log.msg('parse_list_page error:%s' % e)
            return
        for patent in patent_list:
            # url = 'http://search.innojoy.com.cn/CPRS2010/cn/PatentDetails.html?cic=%s&id=%s&idk=%s' % (cic,id,idk)
            # url = ''
            #db = patent.get('DB','')
            #db_name = patent.get('DBName','')

            dn = patent.get('DN', '')
            doc = {
                'data_source': 'innojoy专利搜索',
                'url': 'http://www.innojoy.com/not_exist/%s_0' % dn,
                'applicant_address': patent.get('AR', ''),
                'abstract': patent.get('ABST', ''),
                # '':dic.get('StrAgency',''),
                'agent_institution': patent.get('AGC', ''),
                'agent_person': patent.get('AGT', ''),
                'application_time': patent.get('AD', ''),
                'application_number': patent.get('AN', ''),
                'applicant': patent.get('PA', ''),
                'claims': patent.get('CL', ''),
                'inventor': patent.get('INN', ''),
                'classification': patent.get('PIC', ''),
                'publication_number': patent.get('PNM', ''),
                'publication_time': patent.get('PD', ''),
                'patent_name': patent.get('TI', ''),
                'patent_state': patent.get('LLS', ''),
                'patent_type': patent.get('DBName', ''),
                #---
                'dn': dn,
                'dic': patent,
            }
            image_urls = []
            mp = patent.get('MP', '')
            if mp:
                image_urls.append(mp)

            list_url = response.url
            query = response.meta.get('query')

            db = patent.get('DB', '')
            if not dn or not db:
                next_request = None
            else:
                next_request = self._construct_full_text(dn=dn, db=db)
            item = PatentItem(doc=doc,
                              next_request=next_request, list_url=list_url, query=query,
                              attachments=[], attachment_urls=[])
            item['attachment_urls'] += image_urls
            attachments = item['attachments']
            attach1 = {
                'url': 'http://www.innojoy.com/not_exist/%s_1' % doc.get('dn', ''),
                'data': response.body_as_unicode(),
                'mime_type': get_mime_type_in_response(response)
            }
            attachments.append(attach1)
            yield self.item_or_request(item)

    def parse_full_text(self, response):
        item = response.meta['item']
        doc = item['doc']
        try:
            json_dic = json.loads(response.body_as_unicode())
            if json_dic.get('ErrorInfo', (not None)):
                raise Exception('response json error')
            patent = json_dic['Option']['PatentList'][0]
        except Exception as e:
            log.msg('parse_full_text error %s' % e)
            yield self.item_or_request(item)
            return
        doc['claims'] = patent.get('CLM', '')
        doc['description'] = patent.get('DESCR', '')
        attachments = item['attachments']
        attach1 = {
            'url': 'http://www.innojoy.com/not_exist/%s_2' % doc.get('dn', ''),
            'data': response.body_as_unicode(),
            'mime_type': get_mime_type_in_response(response)
        }
        attachments.append(attach1)
        doc.pop('dic', None)
        doc.pop('dn', None)
        for k, v in doc.items():
            doc[k] = common_clean(v, junks=["<font color='red'>", '</font>'])

        yield self.item_or_request(item)

