#coding=utf8
#!/usr/bin/env python
"""
在鸦的思路中
mechanize,requests,scrapy,webkit都被用到.
因此涉及到大量的内部类转换.例如mechanize的request转换为scrapy的request
在这里为防止requests与request混淆,requests被称为human
"""

from __future__ import division, print_function, unicode_literals
from requests.structures import CaseInsensitiveDict
from scrapy.responsetypes import responsetypes


__metaclass__ = type

#Author:wuya @ smallteam
#Date: 13-5-14

from httplib import responses

from mechanize import make_response
from scrapy.http.request import Request
from requests.models import Response as RequestsResponse


def response_scrapy2requests(scrapy_response):
    """
    非完全的类型转换.小心使用.
    一些属性没有对应赋值
    """
    _content = scrapy_response.body
    headers = CaseInsensitiveDict(headers_scrapy2dict(scrapy_response.headers))
    status_code = scrapy_response.status
    url = scrapy_response.url
    requests_response = RequestsResponse()
    requests_response._content = _content
    requests_response.headers = headers
    requests_response.status_code = status_code
    requests_response.url = url
    requests_response.request = request_scrapy2requests(scrapy_response.request)
    return requests_response


def request_scrapy2requests(scrapy_request):
    #not use yet
    return None


def response_requests2scrapy(requests_response, encoding=None):
    if encoding is not None:
        encoding = encoding
    elif encoding == 'apparent_encoding':
        encoding = requests_response.apparent_encoding
    elif encoding == 'encoding':
        encoding = requests_response.encoding
    else:
        if requests_response.encoding is None:
            encoding = requests_response.encoding
        else:
            encoding = requests_response.apparent_encoding
    url = requests_response.url.encode(encoding)
    status = requests_response.status_code
    headers = dict(requests_response.headers)
    body = requests_response.content
    request = request_requests2scrapy(requests_response.request)
    respcls = responsetypes.from_args(headers=headers, url=url, body=body)
    scrapy_response = respcls(url, status=status, headers=headers, body=body, request=request)
    return scrapy_response


def request_requests2scrapy(requests_request):
    url = requests_request.url
    if isinstance(url, unicode):
        url = url.encode('utf8')
    method = requests_request.method
    headers = dict(requests_request.headers)
    body = requests_request.body
    scrapy_request = Request(url, method=method, headers=headers, body=body)
    return scrapy_request


def request_mechanize2scrapy(mechanize_request, br=None):
    url = mechanize_request.get_full_url()
    method = mechanize_request.get_method()
    headers = mechanize_request.header_items()
    body = mechanize_request.get_data()
    if br:
        br_cj = br._ua_handlers["_cookies"].cookiejar
        cookies = {}
        for c in br_cj:
            cookies[c.name] = c.value
    else:
        cookies = None
    scrapy_request = Request(url, method=method, body=body, headers=headers, cookies=cookies)
    return scrapy_request


def response_scrapy2mechanize(scrapy_response):
    url = scrapy_response.url.encode('utf8')
    code = scrapy_response.status
    msg = responses.get(code, '')
    headers = scrapy_response.headers
    headers = headers_scrapy2mechanize(headers)
    data = scrapy_response.body
    mechanize_response = make_response(data, headers, url, code, msg)
    return mechanize_response


def headers_scrapy2mechanize(scrapy_headers):
    mechanize_headers = []
    for k, v_list in scrapy_headers.iteritems():
        for v in v_list:
            mechanize_headers.append((k, v))
    return mechanize_headers

def headers_scrapy2dict(scrapy_headers):
    dict_headers = {}
    for k, v_list in scrapy_headers.iteritems():
        dict_headers[k] = v_list[-1]
    return dict_headers

def request_scrapy2curl_cmd(scrapy_request):
    cmds = []
    cmds.append('curl')
    cmds.append('"%s"' % scrapy_request.url)
    for k, v_list in scrapy_request.headers.items():
        for v in v_list:
            cmds.append('-H "%s: %s"' % (k, v))
    cmds.append('--data-binary "%s"' % scrapy_request.body)
    cmd = ' '.join(cmds)
    return cmd

