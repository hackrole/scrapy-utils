#coding=utf8
import pymongo
import time
import MySQLdb
import traceback
import logging
import sys
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import *
from selenium.common.exceptions import NoSuchElementException
from xvfbwrapper import Xvfb

con = pymongo.connection.Connection()
db = con.scrapy
coll = db.lunwen

# init the log object
log = logging.getLogger('sel')
log.setLevel(logging.INFO)
#h1 = logging.FileHandler('./run.log')
h1 = logging.StreamHandler(sys.stdout)
h1.setLevel(logging.INFO)
log.addHandler(h1)

# not display the firefox
# comment below to let firefox show
vdisplay = Xvfb()
vdisplay.start()

def get_keyword():
    con2 = MySQLdb.connect(
            host="localhost",
            user='root',
            passwd='root',
            db='ssc',
            charset='utf8'
            )
    cur = con2.cursor(MySQLdb.cursors.DictCursor)
    sql = "select id, keyword from keyword"
    cur.execute(sql)
    result = cur.fetchall()
    return result


def main(w, pro):
    ff = setup(pro)
    input_keword_and_go_to_list(ff, w)
    parse_list_page(ff, w, pro)
    parse_detail_page(ff, w)
    ff.quit()

def setup(pro):
    fp = webdriver.FirefoxProfile()
    #fp.set_preference('permissions.default.stylesheet', 2)
    fp.set_preference('permissions.default.image', 2)
    fp.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    proxy = Proxy({
        'proxyType': ProxyType.MANUAL,
        'httpProxy': pro,
        'ftpProxy': pro,
        'sslProxy': pro,
        'noProxy': ''
        })
    ff = webdriver.Firefox(fp, proxy=proxy)
    #time.sleep(10)
    ff.implicitly_wait(30)
    ff.set_page_load_timeout(100)
    return ff

def input_keword_and_go_to_list(ff, keyword=u"CAD"):
    ff.get('http://www.wanfangdata.com.cn/')
    k = ff.find_element_by_id('queryBox')
    k.send_keys(keyword)
    search = ff.find_element_by_id('searchButton')
    search.click()
    coll.insert({'page':ff.page_source, 'type': 'list', 'pagec': 1, 'kw': keyword})

def parse_list_page(ff, kw, pro=None):
    try:
        for i in range(0, 10):
            current = ff.current_window_handle
            #link_id = "patti%s" % (i,)
            #log.info("the kw: %s, link_id: %s" % (kw, link_id))
            #d_link = ff.find_element_by_id(link_id)
            #link = '//li[@class="title_li"][%s]/a[3]' % (i+1,)
            link = '//*[@id="content_div"]/div[1]/div/ul[%s]/li[1]/a[3]' % (i+1)
            d_link = ff.find_element_by_xpath(link)
            d_link.click()
            ff.switch_to_window(ff.window_handles[1])
            coll.insert({'page':ff.page_source, 'type': 'detail', 'count': i, 'kw': kw})
            ff.close()
            ff.switch_to_window(current)
            time.sleep(2)
    except NoSuchElementException,e:
        print "%s is not a good proxy" % (pro,)
    except Exception, e:
        log.error("error happened, kw: %s, i, %s" % (kw, i))
        log.error(ff.window_handles)
        #traceback.print_exc()
        # error recovery
        if len(ff.window_handles) == 2:
            ff.switch_to_window(ff.window_handles[1])
            ff.close()
            ff.switch_to_window(current)
        time.sleep(600)


def parse_detail_page(ff, kw):
    i = 1
    while True:
        try:
            n_page = ff.find_element_by_link_text("下一页")
            coll.insert({'page':ff.page_source, 'type': 'list', 'pagec': i+1, 'kw': kw})
            log.info(n_page)
            n_page.click()
            parse_list_page(ff, kw)
            i += 1
            print "sleep 10"
            time.sleep(10)
        except Exception, e:
            log.error("parse kw: %s, page: %s error, you should restart from this" % (kw, i+1))
            return
            #sys.exit()


# not user now
def total():
    words = get_keyword()
    for word in words:
        for w in word['keyword'].split('|'):
            try:
                print w
                main(w)
                time.sleep(300)
            except Exception,e:
                log.error("next keyword")

if __name__ == "__main__":
    total()
