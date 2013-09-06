#coding=utf8
#!/usr/bin/env python
"""
这个spider是查询-翻页-进详情页模式的基础spider类.
使用scrapy
如果你使用scrapy+selenium,请注意适配,或使用另一个基础spider类
"""
from __future__ import division, print_function, unicode_literals
from itertools import chain
import re
import urllib
import datetime
import requests
from scrapy.selector import HtmlXPathSelector
from feet8.cells.leg_spider import LegSpider
from feet8.spiders.video_zjcm.utils import VideoZjcmItem, VideoMongodbAdapter

__metaclass__ = type

import json

from scrapy.http import Request


class VideoDetailSpider(LegSpider):
    name = 'video_detail_zjcm'

    start_urls = []
    _item = VideoZjcmItem()
    db_adapter_cls = VideoMongodbAdapter

    def __init__(self, *args, **kwargs):
        super(LegSpider, self).__init__(*args, **kwargs)

    def _get_parse_method(self, site_url):
        method_name = 'parse_%s' % site_url.replace('.', '_')
        parse_method = getattr(self, method_name, None)
        return parse_method

    def start_requests(self):
        docs = self.db_adapter.get_videos(self._item)
        for doc in docs:
            site_url = doc.get('site_url', '')
            parse_method = self._get_parse_method(site_url)
            if not parse_method:
                continue
            url = doc.get('url', '')
            if not url:
                continue
            query = doc.get('query', '')
            item = VideoZjcmItem(doc=doc,
                                 next_request=None, list_url='', query=query,
                                 attachments=[], attachment_urls=[])
            meta = {
                'item': item
            }
            request = Request(url, callback=parse_method, meta=meta)
            # noinspection PyUnresolvedReferences
            request.dont_filter = True
            item['next_request'] = request
            yield self.item_or_request(item)

    def parse_youku_com(self, response):
        hxs = HtmlXPathSelector(response)
        video_id = hxs.re('var videoId.*?(\d+)')[0]

        url_t = "http://v.youku.com/v_vpactionInfo/id/%s"
        url = url_t % (video_id,)
        text = urllib.urlopen(url).read()

        hxs2 = HtmlXPathSelector(text=text)
        pv = hxs2.select('//ul[@class="row"]//span[@class="num"]/text()').extract()[0]
        pv = int(''.join(pv.split(',')))

        # others data
        d_tmp = hxs2.select('//ul[@class="half"]//span/text()').extract()
        # up and down data
        ud = d_tmp[0]
        up, down = d_tmp[0].split('/')
        up, down = int(''.join(up.split(','))), int(''.join(down.split(',')))
        # comments count
        comments = int(''.join(d_tmp[2].split(',')))

        item = response.meta['item']
        doc = item['doc']
        doc['pv'] = pv
        doc['up'] = up
        doc['down'] = down
        doc['comments'] = comments
        return item

    # DONE: raady to check
    def parse_tudou_com(self, response):
        hxs = HtmlXPathSelector(response)
        #video_id = hxs.re(re.compile('iid:\s*(\d+)')
        video_id = hxs.re('iid:\s*(\d+)')[0]
        url_t = "http://www.tudou.com/tva/itemSum.srv?jsoncallback=__TVA_itemSum&iabcdefg=%s&uabcdefg=0&showArea=true&app=5"
        url = url_t % (video_id,)
        data_h = urllib.urlopen(url).read()
        # load as json
        data_h = data_h[data_h.find('(') + 1:data_h.find(')')]

        data_j = json.loads(data_h)
        pv = data_j['playNum']
        up = data_j['digNum']
        down = data_j['buryNum']
        comments = data_j['commentNum']

        item = response.meta['item']
        doc = item['doc']
        doc['pv'] = pv
        doc['up'] = up
        doc['down'] = down
        doc['comments'] = comments
        return item

    def parse_iqiyi_com(self, response):
        hxs = HtmlXPathSelector(response)

        data = hxs.select('//a[@id="j-offline"]')
        aid = ''.join(data.select('./@data-videodownload-albumid').extract())
        url_t = "http://cache.video.qiyi.com/p/%s/"
        u1 = url_t % (aid,)
        r1 = requests.get(u1)
        pv = ''.join(re.findall('"data":(\d+)', r1.text))
        url_t2 = "http://score.video.qiyi.com/ud/%s/"
        u2 = url_t2 % (aid,)
        r2 = requests.get(u2)
        up = ''.join(re.findall('"up":(\d+)', r2.text))
        down = ''.join(re.findall('"down":(\d+)', r2.text))

        comments = 0
        item = response.meta['item']
        doc = item['doc']
        doc['pv'] = pv
        doc['up'] = up
        doc['down'] = down
        doc['comments'] = comments
        return item

    def parse_letv_com(self, response):
        hxs = HtmlXPathSelector(response)

        pid = hxs.re('pid:(\d+)')[0]
        vid = hxs.re('vid:(\d+)')[0]
        mid = hxs.re('mmsid:(\d+)')[0]
        # the pv
        url_t = "http://stat.letv.com/vplay/queryMmsTotalPCount?callback=&cid=1&vid=%s&mid=%s&pid=%s"
        #print "<<<<<<<<<<<<<<<<<<<<<<<<<<<"
        #print pid, vid, mid
        url = url_t % (vid, mid, pid)
        text = urllib.urlopen(url).read()
        pv = re.findall('media_play_count.*?(\d+)', text)[0]
        up = 0
        down = 0

        # the comments count
        url_tt = "http://api.my.letv.com/vcm/api/g?jsonp=&type=video&notice=1&pid=%s&xid=%s&mmsid=%s&rows=10&page=1"
        url2 = url_tt % (pid, vid, mid)
        text2 = urllib.urlopen(url2).read()
        comments = re.findall('total.*?(\d+)', text2)[0]

        item = response.meta['item']
        doc = item['doc']
        doc['pv'] = pv
        doc['up'] = up
        doc['down'] = down
        doc['comments'] = comments
        return item


    def parse_sohu_com(self, response):
        hxs = HtmlXPathSelector(response)

        vid = ''.join(hxs.re('var vid="(\d+)')).strip()
        pid = ''.join(hxs.re('var playlistId="(\d+)')).strip()
        cid = ''.join(hxs.re('var cid="(\d+)')).strip()
        # msg = "sohu id: vid %s, pid %s, cid %s" % (vid, pid, cid)
        # self.log(msg)

        url_t = "http://count.vrs.sohu.com/count/stat.do?videoId=%s&playlistId=%s&categoryId=%s"
        url1 = url_t % (vid, pid, cid)
        text = urllib.urlopen(url1).read()
        pv = ''.join(re.findall('(\d+)', text))

        url_t1 = "http://score.my.tv.sohu.com/digg/get.do?vid=%s&type=%s"
        url1 = url_t1 % (vid, cid)
        text = urllib.urlopen(url1).read()
        t = text[text.find('{'): text.rfind('}') + 1]
        dj = json.loads(t)
        up = dj['upCount']
        down = dj['downCount']

        url_t2 = "http://access.tv.sohu.com/reply/list.do?objid=%s&subobjid=%s&objtype=%s"
        url2 = url_t2 % (pid, vid, cid)
        text = urllib.urlopen(url2).read()
        comments = re.findall('"allCount":(\d+)', text)[0]

        item = response.meta['item']
        doc = item['doc']
        doc['pv'] = pv
        doc['up'] = up
        doc['down'] = down
        doc['comments'] = comments
        return item

    def parse_pptv_com(self, response):
        # pptv没有pv/up/down数据，不做处理
        item = response.meta['item']
        doc = item['doc']
        return item

    def parse_funshion_com(self, response):
        hxs = HtmlXPathSelector(response)

        comments = ''.join(hxs.select('//div[@class="playStarDetails"]/span[1]/span/text()').extract()).strip()
        comments = re.findall('\d+', comments)[0]
        up = 0
        down = 0
        pv = ''.join(hxs.select('//div[@class="playStarDetails"]/span[2]/span/text()').extract()).strip()
        pv = ''.join(pv.split(','))

        item = response.meta['item']
        doc = item['doc']
        doc['pv'] = pv
        doc['up'] = up
        doc['down'] = down
        doc['comments'] = comments
        return item

    def parse_sina_com_cn(self, response):
        hxs = HtmlXPathSelector(response)

        vid = hxs.re('vid:.*?(\d+)\|\d+')[0]
        nid = hxs.re("newsid:'([-\w]+)")[0]
        url_t = "http://count.kandian.com/getCount.php?vids=%s&action=flash"
        url = url_t % ("%s-%s" % (vid, vid))
        data = urllib.urlopen(url).read()
        pv = re.findall('\d+":"(\d+)', data)[0]
        up = 0
        down = 0

        url_tt = "http://comment5.news.sina.com.cn/cmnt/info_wb?channel=movie&newsid=%s&page=1&callback="
        url2 = url_tt % (nid,)
        data2 = urllib.urlopen(url2).read()
        data2 = data2[1:-1]
        dj = json.loads(data2)
        comments = dj["result"]['data']['total_number']

        item = response.meta['item']
        doc = item['doc']
        doc['pv'] = pv
        doc['up'] = up
        doc['down'] = down
        doc['comments'] = comments
        return item

    def parse_kankan_com(self, response):
        hxs = HtmlXPathSelector(response)

        pv = hxs.select('//ul[@id="movie_info_ul"]/li[5]/span/text()').extract()[0]
        pv = ''.join(pv.split(','))
        up = 0
        down = 0

        # TODO comments
        comments = 0

        item = response.meta['item']
        doc = item['doc']
        doc['pv'] = pv
        doc['up'] = up
        doc['down'] = down
        doc['comments'] = comments
        return item

    def parse_wasu_cn(self, response):
        hxs = HtmlXPathSelector(response)

        pv = ''.join(hxs.select('//div[@class="l fun_1"]/text()').extract())
        pv = ''.join(re.findall('([,0-9]+)', pv))
        pv = ''.join(pv.split(','))
        up = ''.join(hxs.select('//span[@id="aup"]/text()').extract())
        down = ''.join(hxs.select('//span[@id="adown"]/text()').extract())
        # TODO:comments, 考虑是否抓取
        comments = 0

        item = response.meta['item']
        doc = item['doc']
        doc['pv'] = pv
        doc['up'] = up
        doc['down'] = down
        doc['comments'] = comments
        return item

    def parse_56_com(self, response):

        # pv, up, down
        video_key = re.findall('v_(\w+).html$', response.url)[0]
        url_t = 'http://stat.56.com/stat/flv.php?id=%s&pct=1'
        url = url_t % (video_key,)  # the url to get pv,down, up
        text = urllib.urlopen(url).read()
        pv = re.findall('times.*?(\d+)', text)[0]
        up = re.findall('ups.*?(\d+)', text)[0]
        down = re.findall('downs.*?(\d+)', text)[0]

        # comment count
        url_tt = "http://comment.56.com/trickle/api/commentApi.php?a=flvLatest&vid=%s.html&pct=1&limit=1"
        url2 = url_tt % (video_key,)
        text2 = urllib.urlopen(url2).read()
        comments = re.findall('pdTotal.*?(\d+)', text2)[0]

        item = response.meta['item']
        doc = item['doc']
        doc['pv'] = pv
        doc['up'] = up
        doc['down'] = down
        doc['comments'] = comments
        return item

    def parse_pps_tv(self, response):
        hxs = HtmlXPathSelector(response)

        video_id = hxs.re("upload_id.*?(\d+)")[0]
        url_t = "http://v.pps.tv/ugc/ajax/ugc.php?type=5&upload_id=%s"
        url = url_t % (video_id,)
        data = json.loads(urllib.urlopen(url).read())
        pv = data["paly_num"]
        up = data["up"]
        down = data["down"]
        comments = data["cmt"]

        item = response.meta['item']
        doc = item['doc']
        doc['pv'] = pv
        doc['up'] = up
        doc['down'] = down
        doc['comments'] = comments
        return item

    def parse_qq_com(self, response):
        hxs = HtmlXPathSelector(response)

        pid = ''.join(hxs.re('id :"(\w+)",'))
        vid = ''.join(hxs.re('vid:"(\w+)",'))

        url_t_1 = "http://sns.video.qq.com/tvideo/fcgi-bin/batchgetplaymount?id=%s&otype=json"
        u1 = url_t_1 % (pid,)
        t1 = urllib.urlopen(u1).read()
        pv = ''.join(re.findall('"num":(\d+)', t1)).strip()

        url_t_2 = "http://sns.video.qq.com/tvideo/fcgi-bin/spvote?&t=3&otype=json&keyid=%s"
        u2 = url_t_2 % (vid,)
        t2 = urllib.urlopen(u2).read()
        tmp = re.findall('"num":(\d+)', t2)
        down, up = tmp

        url_t_3 = "http://sns.video.qq.com/fcgi-bin/liveportal/comment?otype=json&p=1&t=0&sz=10&id=%s"
        u3 = url_t_3 % (pid,)
        t3 = urllib.urlopen(u3).read()
        comments = ''.join(re.findall('"totpg":(\d+)', t3))

        item = response.meta['item']
        doc = item['doc']
        doc['pv'] = pv
        doc['up'] = up
        doc['down'] = down
        doc['comments'] = comments
        return item

    #overload somemethod about item
    # noinspection PyMethodParameters
    def process_item(spider, self):
        now = datetime.datetime.utcnow()
        doc = self['doc']
        #计算部分
        calc_doc = {
        }
        default_doc1 = {
            'crawl_time': now,
        }
        all_doc = chain(calc_doc.iteritems(), default_doc1.iteritems())
        for k, v in all_doc:
            doc.setdefault(k, v)
        doc['attachments'] = self['attachments']
        doc['synced'] = False
