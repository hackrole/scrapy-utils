#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-5-24
"""
"""

from __future__ import division, print_function, unicode_literals
import copy
import datetime
from itertools import chain
import urllib

__metaclass__ = type

import re

from feet8.dbop import upsert_doc
from feet8.utils import fnvhash

company_keys = ['厂', '站', '公司', '事务所', '集团']
contact_res = {
    '联\s*系\s*人\s*[:：]?(.*)': 'shop_contacts',
    '电\s*话\s*[:：]?(.*)': 'shop_phone',
    '联\s*系\s*电\s*话\s*[:：]?(.*)': 'shop_phone',
    '手\s*机\s*[:：]?(.*)': 'shop_cellphone',
    '传\s*真\s*[:：]?(.*)': 'shop_fax',
    'fax\s*[:：]?(.*)': 'shop_fax',
    '地\s*址\s*[:：]?(.*)': 'shop_address',
    '公\s*司\s*地\s*址\s*[:：]?(.*)': 'shop_address',
    'address\s*[:：]?(.*)': 'shop_address',
    '邮\s*箱\s*[:：]?(.*)': 'shop_email',
    'e?[_-＿－]?mail\s*[:：]?(.*)': 'shop_email',
    '公\s*司\s*注\s*册\s*时\s*间\s*[:：]?(.*)': 'shop_launch_time',
}
contact_patterns = {re.compile(k, re.I): v for k, v in contact_res.iteritems()}
qq_url_prefixs = [
    'tencent://message',
    'http://wpa.qq.com',
]
qq_uin_pattern = re.compile(r'uin=(\d+)', re.I)
qq_num_res = [
    r'qq(\d+)'
]
qq_num_patterns = [re.compile(regex, re.I) for regex in qq_num_res]


# noinspection PyDefaultArgument
def clean_string(string, junks=[], no_spaces=True, no_spaces_first=True, maxreplace=-1, not_junks=[]):
    _junks = []
    if no_spaces:
        _junks.extend(['\t', '\n', '\r', ' ', '\u3000'])
    _junks.extend(junks)
    if not no_spaces_first:
        _junks.reverse()
    _junks = [j for j in _junks if j not in not_junks]
    for j in _junks:
        string = string.replace(j, '', maxreplace)
    return string


# noinspection PyDefaultArgument
def clean_shop_products(products, junks=[], not_junks=['\n', '\r' ]):
    products = clean_string(products)
    if junks:
        products = clean_string(products, junks, maxreplace=1)
    return products


def save_company_item(item):
    collection = item['collection']
    doc = item['doc']
    spec = {'shop_site_url_hash': doc['shop_site_url_hash']}
    upsert_doc(collection, spec, doc)


def process_company_item(item, spider):
    now = datetime.datetime.utcnow()
    doc = item['doc']
    #删除部分
    doc.pop('detail_url', None)
    doc.pop('about_url', None)
    doc.pop('contact_url', None)
    #计算部分
    shop_owner_type = calc_shop_owner_type(doc['shop_name'])
    shop_site_url_hash = fnvhash.fnv_64a_str(doc['shop_site_url'])
    calc_doc = {
        'shop_owner_type': shop_owner_type,
        'shop_site_url_hash': str(shop_site_url_hash),
    }
    #提取数据的默认填充部分
    default_doc1 = {
        'crawl_time': now,
        'shop_site_type': spider.shop_site_type,
        'shop_name': None,
        'shop_site_url': None,
        'shop_products': None,
        'shop_launch_time': None,
        'shop_address': None,
        'shop_contacts': None,
        'shop_phone': None,
        'shop_cellphone': None,
        'shop_fax': None,
        'shop_email': None,
        'shop_qq': None,
    }
    #默认填充数据
    default_doc2 = {
        'shop_type_id': None,
        'shop_area_id': None,
        'shop_certified': 1,
        'city_id': 1,
        'is_bad_url': 0,
        'is_bad_time': None,
        'deleted': 0,
        'isRead': 0,
        'isImport': 0,
    }
    all_doc = chain(calc_doc.iteritems(), default_doc1.iteritems(), default_doc2.iteritems())
    for k, v in all_doc:
        doc.setdefault(k, v)


def clean_groups(groups):
    groups = [x for x in groups if len(clean_string(x))]
    return groups



def ana_contact1(groups):
    """
    groups 在一行,例如
    groups1 = [
    '公司名称：	淄博市临淄鲁博厨房设备机械厂',
    '职位：	经理',
    '邮编：	255432',
    ]
    给出结果
    """
    result_dic = {}
    for index, string in enumerate(groups):
        for pattern, var in contact_patterns.iteritems():
            match = pattern.search(string)
            if match:
                value = match.group(1)
                value = value.strip().lstrip(':：').strip()
                if value:
                    result_dic[var] = value
                break
    return result_dic


def ana_contact2(groups):
    """
    groups 在两行,例如
    groups1 = [
    '公司名称：'
    '淄博市临淄鲁博厨房设备机械厂',
    '职位：'
    '经理',
    ]
    给出结果
    """
    result_dic = {}
    for index, string in enumerate(groups):
        for pattern, var in contact_patterns.iteritems():
            match = pattern.search(string)
            if match:
                try:
                    value = groups[index + 1]
                    value = value.strip().lstrip(':：').strip()
                    if value:
                        result_dic[var] = value
                    break
                except IndexError:
                    pass
    return result_dic


# noinspection PyDefaultArgument
def parse_products(hxs, junks=[]):
    groups = hxs.extract()
    groups = clean_groups(groups)
    products = ''.join(groups)
    _junks = copy.copy(junks)
    products = clean_string(products, junks=_junks, no_spaces=False, maxreplace=1)
    return products


def parse_contact(hxs):
    groups = hxs.extract()
    groups = clean_groups(groups)
    groups1 = copy.copy(groups)
    groups2 = copy.copy(groups)
    result_dic = {}
    result_dic1 = ana_contact1(groups1)
    result_dic2 = ana_contact2(groups2)
    result_dic.update(result_dic2)
    result_dic.update(result_dic1)
    return result_dic


def parse_contact1(hxs):
    groups = hxs.extract()
    groups = clean_groups(groups)
    result_dic = ana_contact1(groups)
    return result_dic


def parse_contact2(hxs):
    groups = hxs.extract()
    groups = clean_groups(groups)
    result_dic = ana_contact2(groups)
    return result_dic


def parse_qq_num(hxs):
    #先尝试通过a href解析
    urls = hxs.select('.//a/@href').extract()
    urls = [urllib.unquote(url).strip().lower() for url in urls]
    urls = [url for url in urls if url]
    for url in urls:
        for prefix in qq_url_prefixs:
            if url.startswith(prefix):
                m = qq_uin_pattern.search(url)
                if m:
                    qq = m.group(1)
                    return validate_qq_num(qq)
    #再尝试正则解析
    else:
        text = ''.join(hxs.select('.//text()').extract())
        text = clean_string(text, junks=[':', '：', '号', '号码'])
        for p in qq_num_patterns:
            m = p.search(text)
            if m:
                qq = m.group(1)
                return validate_qq_num(qq)
    return ''


def validate_qq_num(qq):
    is_valid = True
    if not qq.isdigit():
        is_valid = False
    if is_valid:
        return qq
    else:
        return ''


def calc_shop_owner_type(shop_name):
    for k in company_keys:
        if k in shop_name:
            return '公司'
    return '个人'



