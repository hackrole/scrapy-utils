#!/usr/bin/env python
# encoding: utf-8

import requests


start_urls = [
    "http://www.02yyy.com/htm/movielist6",
]

def start_requests(start_urls):
    for urls in self.start_urls:
        response = requests.get(urls)
    parse(response)

def parse(response):
    global url_pool

