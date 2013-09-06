#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-8
"""
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type

from scrapy.item import Item


LENGTH_LIMIT = 50


def _short_item_serializer(value):
    if isinstance(value, unicode):
        if len(value) > LENGTH_LIMIT:
            return b'%s...' % value[:LENGTH_LIMIT].encode('utf8')
        else:
            return value.encode('utf8')
    thing = str(value)
    if len(thing) > LENGTH_LIMIT:
        return b'%s...' % thing[:LENGTH_LIMIT]
    else:
        return thing


class Feet8BaseItem(Item):
    """
    meta反射,可设置默认值
    """

    def __init__(self, *args, **kwargs):
        super(Feet8BaseItem, self).__init__(*args, **kwargs)
        self.set_default_value()
        self.set_short_item_serializer()
        #

    def set_default_value(self):
        """
        谨慎使用这里的default,发现靠不住,感觉多个item间的修改可能被共享-.-
        默认值支持
        """
        for field, meta in self.fields.items():
            try:
                self._values.setdefault(field, meta['default'])
            except KeyError:
                pass

    def set_short_item_serializer(self):
        """
        防止item过长.
        """
        for field, meta in self.fields.items():
            custom_serializer = meta.get('serializer', None)
            if custom_serializer:
                def serializer_ex(value):
                    return _short_item_serializer(custom_serializer(value))
            else:
                serializer_ex = _short_item_serializer
            meta.setdefault('serializer', serializer_ex)



