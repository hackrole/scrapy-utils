#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-7
"""
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type


class SpiderItemMixin():
    """
    提供spider与item相关的交互.相关模块:items.common_item_mixin
    所有调用都走spider,但spider默认会将跟item相关调用委托item自己实现(即通用实现)
    也可重载对应spider,即实现了每spider不同的item调用(即每spider特殊实现).
    """
    db_adapter_cls = None
    db_adapter = None
    _item = None

    _no_duplicate_request = True

    def before_process_item(self, item):
        item.before_process_item(spider=self)

    def process_item(self, item):
        item.process_item(spider=self)

    def after_process_item(self, item):
        item.after_process_item(spider=self)

    def validate_item(self, item):
        return item.validate_item(spider=self)

    def save_item(self, item):
        self.db_adapter.save_item(item, spider=self)

    def save_attachments(self, item):
        self.db_adapter.save_attachments(item)

    def _save_item(self, item):
        self.before_process_item(item)
        self.process_item(item)
        self.after_process_item(item)
        is_valid, msg = self.validate_item(item)
        if is_valid:
            self.save_item(item)
            return True, msg
        else:
            msg = 'validate_item fail,msg:%s' % msg
            return False, msg

    def is_duplicate_request(self, request):
        if self._no_duplicate_request and self._item is not None:
            return self.db_adapter.is_duplicate_request(request, self._item)
        else:
            return False
