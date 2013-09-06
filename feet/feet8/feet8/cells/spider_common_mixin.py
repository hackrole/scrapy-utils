#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-7
"""
"""

from __future__ import division, print_function, unicode_literals
from feet8.utils.mechanize_br import get_br
from feet8.utils.misc import url_chardet

__metaclass__ = type


class SpiderCommonMixin():
    """
    提供功能:
    1,mechanize的延迟加载
    2,与默认编码检测功能
    """
    _site_default_encoding = None
    _br = None


    br = property()

    # noinspection PyRedeclaration
    @br.getter
    def br(self):
        if not self._br:
            self._br = get_br()
        return self._br

    # noinspection PyRedeclaration
    @br.deleter
    def br(self):
        # noinspection PyUnresolvedReferences
        self._br = None

    def _detect_site_default_encoding(self, url):
        #todo fix url_chardet
        if self._site_default_encoding:
            return True
        self._site_default_encoding = url_chardet(url)
        if not self._site_default_encoding:
            return False
        else:
            return True

