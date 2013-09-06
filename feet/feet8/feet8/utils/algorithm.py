#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-19
"""
"""

from __future__ import division, print_function, unicode_literals
from boilerpipe.extract import Extractor

__metaclass__ = type


def get_content(html):
    if not html:
        return ''
    ex = Extractor(extractor='ArticleExtractor', html=html)
    return ex.getText()

def get_text(html):
    if not html:
        return ''
    ex = Extractor(extractor='KeepEverythingExtractor', html=html)
    return ex.getText()