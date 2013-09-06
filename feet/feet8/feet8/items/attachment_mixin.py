#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-3
"""

from __future__ import division, print_function, unicode_literals
from scrapy.item import Field

__metaclass__ = type


class AttachmentMixin():
    attachments = Field(default=[])
    attachment_urls = Field(default=[])