#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-7-1
"""
"""

from __future__ import division, print_function, unicode_literals
import re
from bson import ObjectId
from scrapy.item import Field
from feet8.dbop.db_adapter import DbAdapter
from feet8.dbop.leg_db_adapter import LegDbAdapter
from feet8.items.misc import calc_item_content
from feet8.utils.algorithm import get_content
from feet8.utils.misc import is_duplicate_request_by_url

__metaclass__ = type


import datetime
from itertools import chain

from feet8.utils.digest import url_digest
from feet8.items.doc_item import DocItem

# noinspection PyUnresolvedReferences
from boilerpipe.extract import Extractor






class PatentItem(DocItem):
    collection = Field(default='patent_data')
    item_doc_length = None

    def process_item(self, spider):
        now = datetime.datetime.utcnow()
        doc = self['doc']
        doc.pop('detail_url', None)

        #计算部分
        site_url_hash = url_digest(doc['url'])
        calc_doc = {
            'url_hash':site_url_hash,
        }
        default_doc1 = {
            'spider_name': spider.name,
            'data_type': '专利',
            'crawl_time': now,
            'query': self['query'],

            'patent_name':'',   #专利名称
            'patent_type': '',  #专利类型
            'patent_state': '', #专利状态
            'inventor':'',  #发明人
            'applicant': '',    #申请人
            'applicant_address':'', #地址
            'application_number': '',   #专利号(申请号)
            'application_time':'',  #申请时间
            'publication_number': '',   #公告号
            'publication_time': '', #公告日
            'filing_time': '',  #颁证日
            'agent_person': '', #代理人
            'agent_institution': '',    #代理机构
            'classification': '',   #分类号
            'abstract':'',  #摘要
            'description':'',   #描述
            'claims':'',    #主权项
            'attachments':[],
        }
        all_doc = chain(calc_doc.iteritems(), default_doc1.iteritems())
        for k, v in all_doc:
            doc.setdefault(k, v)
        doc['attachments'] = self['attachments']
        content = calc_item_content(doc, spider)
        doc['content'] = content



class PatentMongodbAdapter(LegDbAdapter):

    correct_dbop_type = 'mongodb'


# noinspection PyDictDuplicateKeys
#[u'agent_institution', u'application_number', u'patent_type', u'classification', u'agent_person', u'publication_number', u'publication_time', u'applicant', u'filing_time', u'applicant_address', u'claims', u'abstract', u'application_time', u'inventor']
patent_regexs = {
    #http://www.soopat.com/ soopat
    '摘\s*要\s*[:：]?(.*)':'abstract',
    '申\s*请\s*人\s*[:：]?(.*)':'applicant',
    '地\s*址\s*[:：]?(.*)':'applicant_address',
    '发\s*明\s*\(\s*设\s*计\s*\)\s*人\s*[:：]?(.*)':'inventor',
    #'主\s*分\s*类\s*号\s*[:：]?(.*)':'',
    '分\s*类\s*号\s*[:：]?(.*)':'classification',
    #'法\s*律\s*状\s*态\s*[:：]?(.*)':'',
    '主\s*权\s*项\s*[:：]?(.*)':'claims',
    '公\s*开\s*号\s*[:：]?(.*)':'publication_number',
    '公\s*开\s*日\s*[:：]?(.*)':'publication_time',
    '专\s*利\s*代\s*理\s*机\s*构\s*[:：]?(.*)':'agent_institution',
    '代\s*理\s*人\s*[:：]?(.*)':'agent_person',
    '颁\s*证\s*日\s*[:：]?(.*)':'filing_time',
    #'优\s*先\s*权\s*[:：]?(.*)':'',
    #'国\s*际\s*申\s*请\s*[:：]?(.*)':'',
    #'国\s*际\s*公\s*布\s*[:：]?(.*)':'',
    #'进\s*入\s*国\s*家\s*日\s*期\s*[:：]?(.*)':'',
    #----------------------------------------------
    #http://so.5ipatent.com/    佰腾网
    '申\s*请\s*号\s*[:：]?(.*)':'application_number',
    '申\s*请\s*日\s*[:：]?(.*)':'application_time',
    '公\s*开\s*/\s*公\s*告\s*号\s*[:：]?(.*)':'publication_number',
    '公\s*开\s*/\s*公\s*告\s*日\s*[:：]?(.*)':'publication_time',
    '申\s*请\s*/\s*专\s*利\s*权\s*人\s*[:：]?(.*)':'applicant',
    '发\s*明\s*/\s*设\s*计\s*人\s*[:：]?(.*)':'inventor',
    #'国\s*际\s*主\s*分\s*类\s*号\s*[:：]?(.*)':'',
    '国\s*际\s*分\s*类\s*号\s*[:：]?(.*)':'classification',
    '地\s*址\s*[:：]?(.*)':'applicant_address',
    #'说\s*明\s*书\s*页\s*数\s*[:：]?(.*)':'',
    #'基\s*本\s*法\s*律\s*状\s*态\s*[:：]?(.*)':'',
    '摘\s*要\s*[:：]?(.*)':'abstract',
    '主\s*权\s*项\s*[:：]?(.*)':'claims',
    #----------------------------------------------
    #http://search.cnpat.com.cn/    专利之星
    '申\s*请\s*号\s*[:：]?(.*)':'application_number',
    '申\s*请\s*日\s*[:：]?(.*)':'application_time',
    '摘\s*要\s*[:：]?(.*)':'abstract',
    '申\s*请\s*人\s*[:：]?(.*)':'applicant',
    #'国\s*家\s*/\s*省\s*市\s*[:：]?(.*)':'',
    '申\s*请\s*人\s*地\s*址\s*[:：]?(.*)':'applicant_address',
    #'主\s*分\s*类\s*号\s*[:：]?(.*)':'',
    '分\s*类\s*号\s*[:：]?(.*)':'classification',
    '公\s*开\s*号\s*[:：]?(.*)':'publication_number',
    '公\s*开\s*日\s*[:：]?(.*)':'publication_time',
    #'授\s*权\s*公\s*告\s*号\s*[:：]?(.*)':'',
    '授\s*权\s*公\s*告\s*日\s*[:：]?(.*)':'filing_time',
    '发\s*明\s*人\s*[:：]?(.*)':'inventor',
    '代\s*理\s*机\s*构\s*[:：]?(.*)':'agent_institution',
    '代\s*理\s*人\s*[:：]?(.*)':'agent_person',
    '独\s*立\s*权\s*利\s*要\s*求\s*[:：]?(.*)':'claims',
    #----------------------------------------------
    #http://search.qianyan.biz/ 钱眼
    '专\s*利\s*号\s*[:：]?(.*)':'application_number',
    '申\s*请\s*日\s*[:：]?(.*)':'application_time',
    '公\s*开\s*/\s*公\s*告\s*日\s*[:：]?(.*)':'publication_time',
    '授\s*权\s*公\s*告\s*日\s*[:：]?(.*)':'filing_time',
    '申\s*请\s*人\s*/\s*专\s*利\s*权\s*人\s*[:：]?(.*)':'applicant',
    #'国\s*家\s*/\s*省\s*市\s*[:：]?(.*)':'',
    '申\s*请\s*人\s*地\s*址\s*[:：]?(.*)':'applicant_address',
    #'邮\s*编\s*[:：]?(.*)':'',
    '发\s*明\s*/\s*设\s*计\s*人\s*[:：]?(.*)':'inventor',
    '代\s*理\s*人\s*[:：]?(.*)':'agent_person',
    '专\s*利\s*代\s*理\s*机\s*构\s*[:：]?(.*)':'agent_institution',
    # '专\s*利\s*代\s*理\s*机\s*构\s*地\s*址\s*[:：]?(.*)':'applicant_address',
    '专\s*利\s*类\s*型\s*[:：]?(.*)':'patent_type',
    '公\s*开\s*号\s*[:：]?(.*)':'publication_number',
    '公\s*告\s*日\s*[:：]?(.*)':'publication_time',
    '授\s*权\s*日\s*[:：]?(.*)':'filing_time',
    # '公\s*告\s*号\s*[:：]?(.*)':'',
    #'优\s*先\s*权\s*[:：]?(.*)':'',
    #'审\s*批\s*历\s*史\s*[:：]?(.*)':'',
    #'附\s*图\s*数\s*[:：]?(.*)':'',
    #'页\s*数\s*[:：]?(.*)':'',
    #'权\s*利\s*要\s*求\s*项\s*数\s*[:：]?(.*)':'',
    #----------------------------------------------
    #http://c.wanfangdata.com.cn/Patent.aspx    万方专利
    '专\s*利\s*类\s*型\s*[:：]?(.*)':'patent_type',
    '申\s*请\s*（\s*专\s*利\s*）\s*号\s*[:：]?(.*)':'application_number',
    '申\s*请\s*日\s*期\s*[:：]?(.*)':'application_time',
    '公\s*开\s*\(\s*公\s*告\s*\)\s*日\s*[:：]?(.*)':'publication_time',
    '公\s*开\s*\(\s*公\s*告\s*\)\s*号\s*[:：]?(.*)':'publication_number',
    #'主\s*分\s*类\s*号\s*[:：]?(.*)':'',
    '分\s*类\s*号\s*[:：]?(.*)':'classification',
    '申\s*请\s*（\s*专\s*利\s*权\s*）\s*人\s*[:：]?(.*)':'applicant',
    '发\s*明\s*（\s*设\s*计\s*）\s*人\s*[:：]?(.*)':'inventor',
    '主\s*申\s*请\s*人\s*地\s*址\s*[:：]?(.*)':'applicant_address',
    '专\s*利\s*代\s*理\s*机\s*构\s*[:：]?(.*)':'agent_institution',
    '代\s*理\s*人\s*[:：]?(.*)':'agent_person',
    #'国\s*别\s*省\s*市\s*代\s*码\s*[:：]?(.*)':'',
    '主\s*权\s*项\s*[:：]?(.*)':'claims',
    #'法\s*律\s*状\s*态\s*[:：]?(.*)':'',
    #----------------------------------------------
    #http://zhuanli.baidu.com/  百度专利
    '申\s*请\s*号\s*/\s*专\s*利\s*号\s*[:：]?(.*)':'application_number',
    '申\s*请\s*日\s*[:：]?(.*)':'application_time',
    '公\s*开\s*日\s*[:：]?(.*)':'publication_time',
    '授\s*权\s*公\s*告\s*日\s*[:：]?(.*)':'filing_time',
    '申\s*请\s*人\s*/\s*专\s*利\s*权\s*人\s*[:：]?(.*)':'applicant',
    '申\s*请\s*人\s*地\s*址\s*[:：]?(.*)':'applicant_address',
    '发\s*明\s*设\s*计\s*人\s*[:：]?(.*)':'inventor',
    '专\s*利\s*代\s*理\s*机\s*构\s*[:：]?(.*)':'agent_institution',
    '代\s*理\s*人\s*[:：]?(.*)':'agent_person',
    '专\s*利\s*类\s*型\s*[:：]?(.*)':'patent_type',
    '分\s*类\s*号\s*[:：]?(.*)':'classification',
    #----------------------------------------------
    #http://www.google.com/patents  google专利    en
    'Publication\s*number\s*[:：]?(.*)':'publication_number',
    'Publication\s*type\s*[:：]?(.*)':'patent_state',
    'Application\s*number\s*[:：]?(.*)':'application_number',
    'Publication\s*date\s*[:：]?(.*)':'publication_time',
    'Filing\s*date\s*[:：]?(.*)':'application_time',
    #'Priority date':'',
    'Also\s*published\s*as\s*[:：]?(.*)':'publication_number',
    'Inventors\s*[:：]?(.*)':'inventor',
    'Applicant\s*[:：]?(.*)':'applicant',
    'International\s*Classification\s*[:：]?(.*)':'classification',
    #http://www.google.com.hk/patents   google专利    中文简体
    '公\s*开\s*号\s*[:：]?(.*)':'publication_number',
    '发\s*布\s*类\s*型\s*[:：]?(.*)':'patent_state',
    '专\s*利\s*申\s*请\s*号\s*[:：]?(.*)':'application_number',
    '公\s*开\s*日\s*[:：]?(.*)':'publication_time',
    '申\s*请\s*日\s*期\s*[:：]?(.*)':'application_time',
    #'优先权日',
    '公\s*告\s*号\s*[:：]?(.*)':'publication_number',
    '发\s*明\s*者\s*[:：]?(.*)':'inventor',
    '申\s*请\s*人\s*[:：]?(.*)':'applicant',
    '国\s*际\s*分\s*类\s*号\s*[:：]?(.*)':'classification',
    #http://www.google.com.hk/patents   google专利    繁体
    '公\s*開\s*號\s*[:：]?(.*)':'publication_number',
    '出\s*版\s*類\s*型\s*[:：]?(.*)':'patent_state',
    '申\s*請\s*書\s*編\s*號\s*[:：]?(.*)':'application_number',
    '發\s*佈\s*日\s*期\s*[:：]?(.*)':'publication_time',
    '申\s*請\s*日\s*期\s*[:：]?(.*)':'application_time',
    # '優先權日期',
    '其\s*他\s*公\s*開\s*專\s*利\s*號\s*[:：]?(.*)':'publication_number',
    '發\s*明\s*人\s*[:：]?(.*)':'inventor',
    '申\s*請\s*者\s*[:：]?(.*)':'applicant',
    '國\s*際\s*專\s*利\s*分\s*類\s*號\s*[:：]?(.*)':'classification',
}
patent_patterns = {re.compile(k): v for k, v in patent_regexs.iteritems()}
strip_values = [
    '专利代理机构地址',
    '专利号',
    '授权公告号',
    '公开(公告)日',
    '国家/省市',
    '申请日',
    '摘要',
    '授权公告日',
    '分类号',
    '申请（专利）号',
    '国际分类号',
    '审批历史',
    '申请日期',
    '进入国家日期',
    '申请号/专利号',
    '国际申请',
    '邮编',
    '申请（专利权）人',
    '申请人地址',
    '国际公布',
    '公开日',
    '公开/公告日',
    '发明(设计)人',
    '申请人',
    '代理人',
    '授权日',
    '公开号',
    '独立权利要求',
    '公开/公告号',
    '优先权',
    '申请/专利权人',
    '公告日',
    '申请人/专利权人',
    '发明人',
    '地址',
    '发明（设计）人',
    '专利代理机构',
    '公告号',
    '附图数',
    '颁证日',
    '代理机构',
    '发明设计人',
    '主分类号',
    '主权项',
    '页数',
    '专利类型',
    '发明/设计人',
    '权利要求项数',
    '法律状态',
    '申请号',
    '公开(公告)号',
    '主申请人地址',
    '专利代理机构',
    '代理人',
    '国别省市代码',
    '主权项',
    '法律状态',
    ':',
    '：',
    '\n',
    '\r',
    '\t',
    ' ',
    '"',
    "'",
    'Publication number',
    'Publication type',
    'Application number',
    'Publication date',
    'Filing date',
    'Priority date',
    'Also published as',
    'Inventors',
    'Applicant',
    'International Classification',
    '公开号',
    '发布类型'
    '专利申请号',
    '公开日',
    '申请日期',
    '优先权日',
    '公告号',
    '发明者',
    '申请人',
    '国际分类号',
    '公開號',
    '出版類型',
    '申請書編號',
    '發佈日期',
    '申請日期',
    '優先權日期',
    '其他公開專利號',
    '發明人',
    '申請者',
    '國際專利分類號',
]

def _blur_ana_patent1(texts):
    result_dic = {}
    for index, string in enumerate(texts):
        for pattern, var in patent_patterns.iteritems():
            match = pattern.search(string)
            if match:
                value = match.group(1)
                value = value.strip().strip(':：').strip()
                for strip in strip_values:
                    value = value.strip(strip)
                if value:
                    result_dic[var] = value
                break
    return result_dic


def _blur_ana_patent2(texts):
    result_dic = {}
    for index, string in enumerate(texts):
        for pattern, var in patent_patterns.iteritems():
            match = pattern.search(string)
            if match:
                try:
                    value = texts[index+1]
                    value = value.strip().strip(':：').strip()
                    for strip in strip_values:
                        value = value.strip(strip)
                    if value:
                        result_dic[var] = value
                    break
                except IndexError:
                    pass
    return result_dic


def blur_ana_patent(texts):
    result_dic = {}
    result_dic1 = _blur_ana_patent1(texts)
    result_dic2 = _blur_ana_patent2(texts)
    result_dic.update(result_dic2)
    result_dic.update(result_dic1)
    return result_dic

