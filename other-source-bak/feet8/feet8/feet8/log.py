#coding=utf8
#!/usr/bin/env python
from __future__ import division, print_function, unicode_literals

__metaclass__ = type

#Author:wuya @ smallteam
#Date: 13-5-17

import logging
import sys
logger = logging.getLogger('land')
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler(stream=sys.stdout)
fmt = "%(levelname)s-%(name)s-%(message)s-%(asctime)s-%(filename)s-%(lineno)d"
stream_fmt = logging.Formatter(fmt)
stream_handler.setFormatter(stream_fmt)
logger.addHandler(stream_handler)