#coding=utf8
#!/usr/bin/env python
from __future__ import division, print_function, unicode_literals
from feet8.utils.digest import url_digest

__metaclass__ = type

#Author:wuya @ smallteam
#Date: 13-5-13

from urlparse import urlparse, urlunparse, parse_qsl
from urllib import urlencode

import requests

from lxml.html import html5parser, tostring
from scrapy.http.request import Request
import io
import lxml.etree as ET
import urllib


def url_chardet(url):
    # noinspection PyBroadException
    try:
        response = requests.get(url)
        return response.encoding
    except Exception:
        return None

_html5parser = html5parser.HTMLParser(namespaceHTMLElements=False)


def text_html5parse(text, encoding='unicode'):
    node = html5parser.fromstring(text, parser=_html5parser)
    etree = node.getroottree()
    parsed = tostring(etree, encoding=encoding)
    return parsed


def response_html5parse(response, no_errors=True):
    """
    这个函数将response中的text替换成经html5parser解析后的内容
    例如添加tbody等,这样chrome和ff生产的xpath就可以直接使用了
    html5解析器还是很接近chrome和ff的解析器的.
    区别在于
    html5解析器对一些地方进行了urlencode,例如a元素的href
    元素大小写略不同
    极少数时候多一两个空格回车什么的.
    元素的属性排列顺序不同.
    """
    text = response.body_as_unicode()
    try:
        new_body = text_html5parse(text, response.encoding)
        parsed = response.replace(body=new_body)
        return parsed
    except Exception as e:
        if no_errors:
            return response
        else:
            raise e

def lxml_etree_from_response(response):
    text = response.body_as_unicode()
    node = html5parser.fromstring(text, parser=_html5parser)
    etree = node.getroottree()
    return etree


def _extract_numbers(s):
    digit_across = ''.join([c if c.isdigit() else '-' for c in s])
    digits = digit_across.split('-')
    digits = [digit for digit in digits if digit]
    return digits


def extract_number(s):
    return int(''.join(_extract_numbers(s)))


def extract_number_list(s):
    return [int(digit) for digit in _extract_numbers(s)]


def get_url_query(url):
    up = urlparse(url)
    query_str = up.query
    query_list = parse_qsl(query_str)
    query_dic = {k: v for k, v in query_list}
    return query_dic


def change_url_query(url,query_dic):
    up = urlparse(url)
    new_up = up[0:4] + (urlencode(query_dic),) + up[5:]
    new_url = urlunparse(new_up)
    return new_url

def get_site_url(url):
    site_url = urlunparse(urlparse(url)[0:2] + ('', '', '', ''))
    return site_url


def fix_possible_missing_scheme(url):
    try:
        Request(url)
        return url
    except ValueError as e:
        if str(e).startswith('Missing scheme in request url'):
            return 'http://%s' % url
        else:
            raise e


def is_duplicate_request_by_url(db_adapter, request, item):
    db = db_adapter.db_mod.db
    collection = item['collection']
    url_hash = url_digest(request.url)
    spec = {'url_hash': url_hash}
    if db[collection].find_one(spec):
        return True
    else:
        return False

def try_int_or_0(value):
    try:
        return int(value)
    except:
        return 0

import datetime
def cal_begin_end_date(begin=None, end=None, interval=None):
    if begin or end:
        return begin, end
    else:
        if interval is not None:
            end = datetime.datetime.today()
            begin = end - datetime.timedelta(days=interval)
            return begin, end
    return begin, end


def get_mime_type_in_response(response):
    headers = response.headers
    content_type = headers.get('content-type', '')
    mime_type = content_type.split(';')[0]
    return mime_type