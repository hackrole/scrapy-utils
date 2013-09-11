#!/usr/bin/env python
# encoding: utf-8

from scrapy.spider import BaseSpider
from module import Stuff


class PerSpider(BaseSpider):
    """ spider  with personal settings,配合user_command使用 """
    custom_settings = {}
    name = ""

    def __init__(self, *arg, **kw):
        """
        """
        pass

class KeySpider(PerSpider):
    """spider for keywords search and list parse to details"""

    def __init__(self):
        """ to be defined1 """
        # TODO
        pass


    def get_keywords(self):
        """
        get the keywords as a iterable object
        """
        raise NotImplented()

    def keywordToURL(self, keyword):
        """ keyword to URL"""
        raise NotImplented()

    def page_next(self):
        """
        go to the next page
        """
        raise NotImplented()

    def parse_detail(self):
        """
        parse detail page, return items
        """
        raise NotImplented()

    def star_requests(self):
        keywords = self.get_keywords()

        for keyword in keywords:
            url = self.keywordToURL(keyword)


