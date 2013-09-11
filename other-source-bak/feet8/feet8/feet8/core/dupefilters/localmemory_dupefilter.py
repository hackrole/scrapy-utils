#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-23
"""

from __future__ import division, print_function, unicode_literals
import traceback
from scrapy.dupefilter import BaseDupeFilter
from feet8.utils.digest import request_digest

__metaclass__ = type

import os
from cityhash import CityHash64, CityHash128


class LocalmemoryDupefilter(BaseDupeFilter):
    """Request Fingerprint duplicates filter"""

    def __init__(self, settings):
        self.file = None
        self.fingerprints = set()
        path = settings.get('DUPEFILTER_FILE', '')
        method_name = settings.get('DUPEFILTER_METHOD', 'cityhash64')
        history_size = settings.get('DUPEFILTER_HISTORY', 50000000)
        max_size = settings.get('DUPEFILTER_MAX', history_size * 2)
        self.path = path
        self.method_name = method_name
        self.history_size = history_size
        self.max_size = max_size
        if method_name == 'cityhash64':
            self.method = CityHash64
        elif method_name == 'cityhash128':
            self.method = CityHash128
        else:
            self.method = CityHash64
        if path:
            self.file = open(path, 'w+')
            for line in list(self.file)[-history_size:]:
                try:
                    self.fingerprints.add(int(line.rstrip()))
                    self.file.write(line)
                except Exception as e:
                    #todo debug
                    traceback.print_exc()
                    continue

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

    def request_seen(self, request):
        fp = request_digest(request, self.method)
        fingerprints = self.fingerprints
        if fp in fingerprints:
            return True

        fingerprints.add(fp)
        if self.file:
            self.file.write(str(fp) + os.linesep)
        if len(fingerprints) > self.max_size:
            pop_size = self.max_size // 10
            pop_size = pop_size if pop_size else 1
            for x in pop_size:
                fingerprints.pop()
        return False

    def close(self, reason):
        if self.file:
            self.file.close()
