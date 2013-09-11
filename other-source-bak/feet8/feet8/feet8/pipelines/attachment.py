#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-1
"""

from __future__ import division, print_function, unicode_literals
from bson import Binary
from scrapy.contrib.linkextractors.lxmlhtml import LxmlParserLinkExtractor

from scrapy.http import Request, TextResponse
from feet8.utils.misc import get_mime_type_in_response

__metaclass__ = type

from scrapy.contrib.pipeline.media import MediaPipeline


class AttachmentPipeLine(MediaPipeline):
    UPDATE_ATTACHMENT = False

    @classmethod
    def from_settings(cls, settings):
        cls.UPDATE_ATTACHMENT = settings.getbool('UPDATE_ATTACHMENT', False)
        return cls()

    def process_item(self, item, spider):
        new_attachments = []
        for attach in item.get('attachments', []):
            attach_id = spider.db_adapter.save_attachment(attach)
            new_attachments.append(attach_id)
        item['attachments'] = new_attachments
        return super(AttachmentPipeLine, self).process_item(item, spider)

    def get_media_requests(self, item, info):
        attachment_urls = item.get('attachment_urls', [])
        attachment_urls = list(set(attachment_urls))
        spider = info.spider
        for url in attachment_urls:
            if not self.UPDATE_ATTACHMENT and spider.db_adapter.find_attachment_by_url(url):
                item['attachments'].append(url)
            else:
                meta = {'item': item}
                yield Request(url, meta=meta)

    def media_downloaded(self, response, request, info):
        item = response.meta['item']
        if isinstance(response, TextResponse):
            data = response.body_as_unicode()
        else:
            data = Binary(response.body)
        attach = {
            'url': request.url,
            'data': data,
            'mime_type': get_mime_type_in_response(response),
        }
        attach_id = info.spider.db_adapter.save_attachment(attach)
        item['attachments'].append(attach_id)
        return response

    def media_failed(self, failure, request, info):
        #todo 这里错误处理不知道怎么搞的,现在如果有一个错误的url将会导致item无法return
        #fixit,在发起请求时判断url是否异常?
        #最好是什么样忽略掉这个异常.
        # return failure
        return None

    def item_completed(self, results, item, info):
        attachments = item.get('attachments', [])
        item['attachments'] = list(set(attachments))
        return item


def get_image_urls(response):
    #sgml seems not work.htmlparser slow than lxml.user lxml
    # img_ex = SgmlLinkExtractor(allow=(), tags=('img',), attrs=('src',))
    # img_ex = HtmlParserLinkExtractor(tag='img', attr='src', unique=True)
    img_ex = LxmlParserLinkExtractor(tag='img', attr='src', unique=True)
    links = img_ex.extract_links(response)
    urls = [link.url for link in links]
    return urls

