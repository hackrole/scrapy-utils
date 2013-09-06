#coding=utf8
#!/usr/bin/env python
#Author:wuya @ smallteam
#Date: 13-6-19
"""
"""

from __future__ import division, print_function, unicode_literals

__metaclass__ = type

def no_readonly(form):
    for control in form.controls:
        control.readonly = False

def no_disable(form):
    for control in form.controls:
        control.disabled = False

def activate_controls(form):
    no_disable(form)
    no_readonly(form)
