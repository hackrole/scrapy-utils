#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-19
"""
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type

class DbAdapter():

    correct_dbop_type = None

    def __init__(self, db_mod, dbop_type):
        correct_dbop_type = self.correct_dbop_type
        if correct_dbop_type is not None and correct_dbop_type != dbop_type:
            raise Exception('DbAdapter,dbop_type mismatch')
        self.db_mod = db_mod
        self.dbop_type = dbop_type