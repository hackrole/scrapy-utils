#!/usr/bin/env python
#coding=utf-8

import gevent
from gevent import monkey
monkey.patch_all()

import re
import db
import ujson as json
import magic
import random
import config
import urlnorm
import requests
import cityhash
import encoding
import lxml.html
import lxml.html.clean
import tldextracter
from logger import logger
from useragents import USER_AGENTS
from rulers import RULERS


title_match = re.compile(r'<title>(.*?)</title>', re.IGNORECASE)
url_match = re.compile(r'#.*', re.DOTALL)

cleaner = lxml.html.clean.Cleaner(
    scripts=True,
    javascript=True,
    comments=True,
    style=True,
    links=True,
    meta=True,
    page_structure=True,
    processing_instructions=True,
    embedded=True,
    frames=True,
    forms=True,
    annoying_tags=True,
    remove_tags=None,
    allow_tags=None,
    kill_tags=None,
    remove_unknown_tags=True,
    safe_attrs_only=True,
    safe_attrs=frozenset(['abbr', 'accept', 'accept-charset']),
    add_nofollow=False,
    host_whitelist=(),
    whitelist_tags=set(['embed', 'iframe']),
    _tag_link_attrs={'a': 'href', 'applet': ['code', 'object']})


def fetch(url, use_proxy=True, timeout=None, headers={}):
    status, content = 408, ''
    timeout = timeout or config.TIMEOUT
    headers = headers or config.HEADERS
    useragent = random.randint(0, len(USER_AGENTS)-1)
    headers["user-agent"] = useragent
    if use_proxy:
        proxies = db.get_proxies()
        try:
            with gevent.Timeout(config.TIMEOUT, Exception):
                r = requests.get(url, stream=False, verify=False,
                                 timeout=timeout, headers=headers,
                                 proxies=proxies)
        except Exception, e:
            print e
            return status, content
    else:
        try:
            with gevent.Timeout(config.TIMEOUT, Exception):
                r = requests.get(url, stream=False, verify=False,
                                 timeout=timeout, headers=headers)
        except Exception, e:
            print e
            return status, content
    return r.status_code, r.content


def process(func, *args, **kwargs):

    def wrapper(*args, **kwargs):
        url, urlhash, status, domain, content = func(*args, **kwargs)
        if not content or not isinstance(content, unicode):
            return []
        try:
            url = url.encode('utf8')
        except Exception, e:
            print e
        rootdomain = tldextracter.extract_rootdomain(url)
        if not rootdomain:
            return []
        try:
            absolute_content = lxml.html.make_links_absolute(content, url)
            tree = lxml.html.fromstring(absolute_content)
        except Exception, e:
            print e
            return []

        #extract content
        cleaned = cleaner.clean_html(content)
        raw_text = lxml.html.fromstring(cleaned).text_content()

        try:
            title = title_match.findall(content)[0]
        except Exception, e:
            print e
            title = ''

        print 'raw', raw_text, 'title', title
        '''
        try:
            db.insert(urlhash, html, title, raw_text)
        except Exception, e:
            print e, type(url)
        '''

        #extract links
        elems = tree.xpath('//a[@href]')
        urls = map(lambda a: a.attrib['href'], elems)
        urls = list(set(urls))
        filtered_urls = []
        for _url in urls:
            _url = url_match.sub('', _url)
            try:
                _url = urlnorm.norm(_url)
            except Exception, e:
                print e
                continue
            for prefix in RULERS[rootdomain]["rulers"]:
                if _url.startswith(prefix):
                    filtered_urls.append(_url)
                    break
        try:
            map(db.push, filtered_urls)
        except Exception, e:
            print e

        return filtered_urls
    return wrapper


@process
def handle(job, *args, **kwargs):
    print 'handle', args, kwargs
    task = json.loads(job)
    url = task["url"]
    domain = tldextracter.extract_domain(url)
    status, content = fetch(url, use_proxy=False)
    try:
        url = url.encode('utf8')
        urlhash = cityhash.CityHash64(url)
    except:
        return (url, None, status, domain, content)
    logger.info('%s|%s' % (url, status))
    if magic.from_buffer(content, mime=True) != 'text/html':
        return (url, urlhash, status, domain, content)
    _, content = encoding.html_to_unicode('', content)
    if status != 200:
        db.push(url, detail=False)
        return (url, urlhash, status, domain, content)
    return (url, urlhash, status, domain, content)


if __name__ == '__main__':
    #pass
    job = {"url": "http://whyfiles.org"}
    handle(json.dumps(job))
