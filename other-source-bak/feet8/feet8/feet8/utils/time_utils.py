#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-6-26
"""

from __future__ import division, print_function, unicode_literals

from dateutil.tz import gettz, tzlocal
# from dateutil.zoneinfo import gettz

__metaclass__ = type

import arrow
import string
import parsedatetime as pdt

c = pdt.Constants('zh_cn')
p = pdt.Calendar(c)

#todo6+36+中文数字2阿拉伯数字

def _fix_time_str1(time_str):
    fix_table = {
        '01月': '1月',
        '02月': '2月',
        '03月': '3月',
        '04月': '4月',
        '05月': '5月',
        '06月': '6月',
        '07月': '7月',
        '08月': '8月',
        '09月': '9月',
    }
    for k, v in fix_table.items():
        time_str = time_str.replace(k, v)
    return time_str


def _fix_time_str2(time_str):
    pre_condition = ['前', '后']
    for pre in pre_condition:
        if pre in time_str:
            break
    else:
        return ''
    fix_table = {
        '天': 'days',
        '时': 'hours',
        '分': 'minutes',
        '秒': 'seconds',
        '前': 'before',
        '后': 'after',
    }
    for k, v in fix_table.items():
        time_str = time_str.replace(k, v)
    return time_str


def _fix_time_str3(time_str, strict=False):
    fix_table = {
        '前天':'2 days before',
        '昨天':'1 days before',
        '今天':'today',
        '明天':'1 days after',
        '后天':'2 days after',
    }
    if strict:
        for k, v in fix_table.items():
            if time_str == k:
                return v
    else:
        for k, v in fix_table.items():
            if time_str.find(k) != -1:
                return v
    return ''


def parse_time(time_str):
    # 0 = not parsed at all
    # 1 = parsed as a C{date}
    # 2 = parsed as a C{time}
    # 3 = parsed as a C{datetime}
    fix_time_str3 = _fix_time_str3(time_str)
    if fix_time_str3:
        return p.parse(fix_time_str3)
    fix_time_str2 = _fix_time_str2(time_str)
    if fix_time_str2:
        return p.parse(fix_time_str2)
    fix_time_str1 = _fix_time_str1(time_str)
    return p.parse(fix_time_str1)

def arrow_parse_time(time_str):
    result = parse_time(time_str)
    tzinfo = tzlocal()
    return arrow.Arrow(*(result[0][:7]), tzinfo=tzinfo)


if __name__ == '__main__':
    print(parse_time('06月23日 08:20 '))
    print(parse_time('21分钟前'))
    print(parse_time('2天前'))
    a=arrow_parse_time('06月23日 08:20 ')
    b=arrow_parse_time('21分钟前')
    c=arrow_parse_time('2天前')
    print(a)
    print(b)
    print(c)