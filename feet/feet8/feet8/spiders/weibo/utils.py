#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-3
"""
"""

from __future__ import division, print_function, unicode_literals

import random

from scrapy import log
from scrapy.item import Field
from feet8.dbop.db_adapter import DbAdapter
from feet8.utils.mechanize_br import get_br
from feet8.utils.misc import get_url_query, change_url_query

__metaclass__ = type


import datetime
from itertools import chain

from feet8.items.doc_item import DocItem

def caiban_sina_weibo_login(user, pw):
    encoding = 'utf8'
    br = get_br()
    try:
        br.open('http://weibo.cn/')
        br.follow_link(text='登录'.encode(encoding))
    except Exception as e:
        return '', str(e)
    form = list(br.forms())[0]
    user_control = form.controls[0]
    pw_control = form.controls[1]
    # remember_control = form.controls[2]
    user_control.value = user.encode(encoding)
    pw_control.value = pw.encode(encoding)
    #default is on
    #remember_control.value = ['on',]
    try:
        br.open(form.click())
    except Exception as e:
        return '', str(e)
    url = br.geturl()
    gsid = get_url_query(url).get('gsid', '')
    # url = 'http://weibo.cn/?gsid=%(gsid)s&vt=4' % {'gsid': gsid}
    # br.open(url)
    content = br.response().read().decode(encoding, 'ignore')
    if content.find('请输入图片中的字符')!=-1:
        reason = 'yzm'
    elif content.find('您的微博帐号出现异常被暂时冻结')!=-1:
        reason = 'freeze'
    elif content.find('@我的')!=-1:
        reason = 'success'
    elif content.find('登录名或密码错误')!=-1:
        reason = 'auth fail'
    elif url.find('http://login.weibo.cn/login')!=-1:
        reason = 'fail'
    elif url.find('http://weibo.cn/pub/')!=-1:
        reason = 'redirect'
    else:
        reason = 'unknown'
    return gsid, reason

class SinaGsid():
    gsid = None
    times = 0
    user = ''
    pw = ''

    def __init__(self, gsid, times, user, pw):
        self.gsid = gsid
        self.times = times
        self.user = user
        self.pw = pw


class CaibanSinaWeiboMiddleware(object):

    def __init__(self, crawler):
        settings =crawler.settings
        self.users = settings.get('USERS', [])
        self.gsid_max_times = settings.getint('GSID_MAX_TIMES', 10000)
        self.gsids = {}
        for user, pw in self.users:
            self._login(user, pw)

    def _choose_gsid(self):
        try:
            gsid = random.choice(self.gsids.keys())
        except IndexError:
            gsid = ''
        finally:
            # noinspection PyUnboundLocalVariable
            return gsid

    def _minus_gsid_times(self, gsid):
        sina_gsid = self.gsids.get(gsid, None)
        if not sina_gsid:
            return
        sina_gsid.times -=-1
        if sina_gsid.times <= 0:
            self.gsids.pop(gsid, None)
            self._login(sina_gsid.user, sina_gsid.pw)

    def _login(self, user, pw):
        gsid, reason = caiban_sina_weibo_login(user, pw)
        if gsid and reason in ['success']:
            sina_gsid = SinaGsid(gsid,self.gsid_max_times,user,pw)
            self.gsids[gsid] = sina_gsid
        else:
            log.msg('CaibanSinaWeiboMiddleware,%s login fail' % user)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def _get_request_gsid(self, request):
        url_gsid = get_url_query(request.url).get('gsid', '')
        cookies_gsid = ''
        meta_gsid = request.meta.get('gsid', '')
        referer = request.headers.get('referer', '')
        referer_gsid = get_url_query(referer).get('gsid', '')
        return url_gsid, cookies_gsid, meta_gsid, referer_gsid

    def process_request(self, request, spider):
        """
        当前未使用cookies
        """
        url_gsid, cookies_gsid, meta_gsid, referer_gsid = self._get_request_gsid(request)
        if url_gsid or cookies_gsid:
            return
        elif meta_gsid:
            gsid = meta_gsid
        elif referer_gsid:
            gsid = referer_gsid
        else:
            gsid = self._choose_gsid()
        if not gsid:
            log.msg('CaibanSinaWeiboMiddleware,no gsid')
            return
        self._minus_gsid_times(gsid)
        raw_url = request.url
        query_dic = get_url_query(raw_url)
        query_dic['gsid'] = gsid
        new_url = change_url_query(raw_url, query_dic)
        new_meta = request.meta
        new_meta['gsid'] = gsid
        new_request = request.replace(url=new_url,meta=new_meta)
        return new_request


class WeiboItem(DocItem):
    collection = Field(default='weibo_data')
    item_doc_length = None

    def process_item(self, spider):
        now = datetime.datetime.utcnow()
        doc = self['doc']
        #计算部分
        calc_doc = {
        }
        #提取数据的默认填充部分
        default_doc1 = {
            'spider': spider.name,
            'data_type': '微博',
            'crawl_time': now,
            'query': self['query'],
        }
        all_doc = chain(calc_doc.iteritems(), default_doc1.iteritems())
        for k, v in all_doc:
            doc.setdefault(k, v)


class WeiboMongodbAdapter(DbAdapter):

    correct_dbop_type = 'mongodb'

    def save_item(self, item):
        db = self.db_mod.db
        collection = item['collection']
        doc = item['doc']
        spec = {'own_user_id':doc['own_user_id'],'own_msg_id':doc['own_msg_id'],}
        db[collection].update(spec, doc, upsert=True, w=0)
