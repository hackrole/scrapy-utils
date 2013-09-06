#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-5
"""
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type

def get_obj_attrs(obj):
    attrs = getattr(obj, '__dict__', {})
    attrs_dic = {}
    for k, v in attrs.items():
        if callable(v):
            pass
        else:
            attrs_dic[k] = v
    attrs_dic.pop('__dict__', None)
    return attrs_dic