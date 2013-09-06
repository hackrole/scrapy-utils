#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-17
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type
from string import whitespace


def common_clean(string, junks=[], no_spaces='sides'):
    if not isinstance(string,basestring):
        return ''
    if no_spaces == 'sides':
        string = string.strip()
    if no_spaces == 'all':
        junks.extend(whitespace)
    for junk in junks:
        string = string.replace(junk, '')
    return string
