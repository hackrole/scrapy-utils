#!/usr/bin/env python
#coding=utf8

from os import path
import random

def new_select(hxs, xpath, join_str=''):
    l = hxs.select(xpath).extract()
    ll = [i.strip() for i in l if i.strip()]

    result = join_str.join(ll).strip()
    return result

def load_item(db_date, hxs, item_t):
    item = item_t()
    for i in db_date:
        item[i['name']] = new_select(hxs, i['xpath'], i['join'])

    return item

def random_proxy():
    p1 = path.dirname(path.realpath(__file__))
    p2 = path.join(p1, '../../proxy_use.txt')
    proxy_file = open(p2)
    proxys = []
    for i in proxy_file.readlines():
        proxy = i.split('\t')[0].strip()
        proxys.append(proxy)


    l = len(proxys)
    pro = proxys[random.randint(0, l-1)]
    return "http://%s" % (pro,)


