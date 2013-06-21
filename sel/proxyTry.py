#coding=utf
import traceback
from selenium import webdriver
from selenium.webdriver.common.proxy import *
from xvfbwrapper import Xvfb

# not display the firefox
# comment below to let firefox show
vdisplay = Xvfb()
vdisplay.start()

f = open('./proxy_use.txt', 'a')

URL_TRY = 'http://s.wanfangdata.com.cn/Paper.aspx?q=%E6%95%B0%E5%AD%97%E5%8C%96%E5%88%B6%E9%80%A0'

def test(pro):
    if not pro:
        print "empty"
        return
    try:
        fp = webdriver.FirefoxProfile()
        fp.set_preference('permissions.default.stylesheet', 2)
        fp.set_preference('permissions.default.image', 3)
        fp.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        proxy = Proxy({
            'proxyType': ProxyType.MANUAL,
            'httpProxy': pro,
            'ftpProxy': pro,
            'sslProxy': pro,
            'noProxy': ''
            })
        ff = webdriver.Firefox(fp, proxy=proxy)
        ff.set_page_load_timeout(5)
        ff.get(URL_TRY)
        ff.quit()
        print "%s a good proxy" % (pro,)
        s = pro +'\n'
        f.write(s)
        f.flush()
    except Exception,e:
        print "%s not a good proxy" % (pro,)
        print traceback.format_exc()

def main():
    pro_b = open('proxy.txt').readlines()
    pro = []
    for i in pro_b:
        pro.append(i.strip('\n '))

    for i in pro:
        test(i)

if __name__ == "__main__":
    main()
