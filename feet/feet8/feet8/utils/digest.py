#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-3
"""
"""

from __future__ import division, print_function, unicode_literals
from scrapy.utils.url import canonicalize_url

__metaclass__ = type


from scrapy.utils.request import _fingerprint_cache
from cityhash import CityHash64
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

def url_digest(url):
    if isinstance(url,unicode):
        url = url.encode('utf8')
    if not isinstance(url, basestring):
        return ''
    url = canonicalize_url(url)
    digest = CityHash64(url)
    digest = hex(digest)
    digest = digest.lstrip('0x').rstrip('L')
    return digest


def request_digest(request, method, include_headers=None,):
    """
    同scrapy自带的request_fingerprint
    可定制使用的method,如cityhash64,cityhash128
    """
    if include_headers:
        include_headers = tuple([h.lower() for h in sorted(include_headers)])
    cache = _fingerprint_cache.setdefault(request, {})
    if include_headers not in cache:
        buff = StringIO()
        buff.write(request.method)
        buff.write(canonicalize_url(request.url))
        buff.write(request.body or '')
        if include_headers:
            for hdr in include_headers:
                if hdr in request.headers:
                    buff.write(hdr)
                    for v in request.headers.getlist(hdr):
                        buff.write(v)
        cache[include_headers] = method(str(buff))
    return cache[include_headers]

