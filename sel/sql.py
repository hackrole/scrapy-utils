#coding=utf8
import pymongo
import logging
import re
import traceback
from sqlalchemy import create_engine
from scrapy.selector import HtmlXPathSelector

logging.basicConfig(filename='./sqlachemy.log', filemode='w')
logging.getLogger('sqlalchemy.emgine').setLevel(logging.INFO)

mysql_str = "mysql://root:root@localhost/ssc?charset=utf8"
engine = create_engine(mysql_str, echo=True)
mysql_con = engine.connect()

def get_data_from_mongo():
    mongo_con = pymongo.connection.Connection()
    mongo_db = mongo_con.zl
    mongo_t = mongo_db.page_dev
    result = mongo_t.find({'type':'detail'})
    return result

def page_parse(page, kw):
    hxs = HtmlXPathSelector(text=page)
    tb1 = hxs.select('//table[@class="xilanneirong"]')
    tr1 = tb1.select('.//tr[1]')
    d_no = ''.join(tr1.select('./td[1]/span/text()').extract())
    app_time = ''.join(tr1.select('./td[2]/span/text()').extract())
    app_time = '-'.join(app_time.split('.'))
    pub_time = ''.join(tr1.select('./td[4]/span/text()').extract())
    pub_time = '-'.join(pub_time.split('.'))

    app_name = ','.join(tb1.select('.//tr[2]/td/span/a/text()').extract())
    app_desirer = ','.join(tb1.select('.//tr[3]/td[1]/span/a/text()').extract())
    app_addr = ''.join(tb1.select('.//tr[4]/td[1]/span/text()').extract())
    type_name = kw
    type_no = ';'.join(tb1.select('.//tr[5]/td[1]/span/text()').extract())

    tb2 = hxs.select('//table[@class="xilanneirong mo"]')
    d_desc = ''.join(tb2.select('.//tr[2]/td[1]/span/text()').extract())
    d_name = ''.join(hxs.select('//div[@class="zhuanli_name"]/text()').extract())

    proxy_agent = ''
    proxy_name = ''
    level_time = ''

    item = {}
    item['url_hash'] = ''
    item['d_name'] = d_name
    item['d_desc'] = d_desc

    item['d_no'] = d_no
    item['app_time'] = app_time
    item['pub_time'] = pub_time
    item['level_time'] = level_time

    item['app_name'] = app_name
    item['app_addr'] = app_addr
    item['app_desirer'] = app_desirer
    item['proxy_gent'] = proxy_agent
    item['proxy_name'] = proxy_name
    item['type_name'] = type_name
    item['type_no'] = type_no

    return item

def sql_insert(item):
    sql2 = "select d_no from demo_result where d_no = '%s'" % (item['d_no'],)
    result2 = mysql_con.execute(sql2).fetchall()
    print result2

    if result2:
        print 'd_no: %s exists' % (item['d_no'],)
        return

    sql = """insert into demo_result (url_hash, d_name, d_desc, d_no,
        app_time, pub_time, level_time, app_name, app_addr, app_desirer,
        proxy_gent, proxy_name, type_name, type_no)
        values ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")""" % (
        item['url_hash'],
        item['d_name'],
        item['d_desc'],
        item['d_no'],
        item['app_time'],
        item['pub_time'],
        item['level_time'],
        item['app_name'],
        item['app_addr'],
        item['app_desirer'],
        item['proxy_gent'],
        item['proxy_name'],
        item['type_name'],
        item['type_no'])
    result = mysql_con.execute(sql)
    #engine.commit()
    print "save item finish"
    return result

def main():
    data = get_data_from_mongo()
    j = 0;
    for i in range(data.count()):
        d = data.next()
        print len(d['page'])
        print type(d['page'])
        if len(d['page']) >=30000: j+=1
        if not re.findall('</html>', d['page']): print "not match";continue
        try:
            print d['kw']
            page = d['page']
            item = page_parse(page, d['kw'])
            sql_insert(item)
        except Exception,e:
            print e.message
            print traceback.format_exc()

    print i,j




if __name__ == "__main__":
    main()


