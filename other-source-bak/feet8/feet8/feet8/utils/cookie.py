#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-12
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type

def dict2str(cookie_dict):
    cookie_list = []
    for k,v in cookie_dict.items():
        cookie_list.append('%s=%s'%(k,v))
    return ';'.join(cookie_list)
