#coding=utf8
#!/usr/bin/env python
"""
Author:wuya @ smallteam
Date: 13-7-12
"""

from __future__ import division, print_function, unicode_literals
import json
from requests.utils import guess_json_utf

__metaclass__ = type


def loads(*args, **kwargs):
    on_error = kwargs.pop('on_error', None)
    try:
        return json.loads(*args, **kwargs)
    except Exception as e:
        return on_error
#
# def _json_loads(text,content,**kwargs):
#     """Returns the json-encoded content of a response, if any.
#
#     :param \*\*kwargs: Optional arguments that ``json.loads`` takes.
#     """
#
#     if not self.encoding and len(self.content) > 3:
#         # No encoding set. JSON RFC 4627 section 3 states we should expect
#         # UTF-8, -16 or -32. Detect which one to use; If the detection or
#         # decoding fails, fall back to `self.text` (using chardet to make
#         # a best guess).
#         encoding = guess_json_utf(self.content)
#         if encoding is not None:
#             return json.loads(self.content.decode(encoding), **kwargs)
#     return json.loads(self.text or self.content, **kwargs)