#!/usr/bin/env python
#coding=utf8

import requests
import time
import traceback
from scrapy.selector import HtmlXPathSelector
from requests.exceptions import ConnectionError, Timeout

proxy_file = "proxy.txt"
test_url = "http://www.wanfangdata.com.cn/"
save_file = "proxy_ok.txt"
time_out = 5

def main():
    f = open(proxy_file)
    sf = open(save_file, 'w')
    proxy_l = [ i.strip('\n ') for i in f.readlines() ]

    for i in proxy_l:
        try:
            proxy = {'http': i}
            cur_time = time.time()
            result = requests.get(test_url, proxies=proxy, timeout=time_out)
            re_time = time.time() - cur_time
            cr, tt = check_wanfang(result.text)
            if cr:
                print "%s is a good proxy: %s" % (i, re_time,)
                msg = '%s\t%s\n' % (i, re_time)
                sf.write(msg)
                sf.flush()
            else:
                print "%s is a bad proxy: %s:%s" % (i, re_time, tt,)
        except ConnectionError, e:
            print "%s is a bad proxy" % (i,)
            #traceback.print_exc()
        except Timeout, e:
            print "%s link time out" % (i,)
        except Exception, e:
            traceback.print_exc()





def check_wanfang(text, xpath="//title/text()", title=u"万方数据知识服务平台"):
    hxs = HtmlXPathSelector(text=text)
    t = ''.join(hxs.select(xpath).extract()).strip('\r\t\n ')
    if t == title:
        return (1,t)
    else:
        return (0,t)

if __name__ == "__main__":
    main()
