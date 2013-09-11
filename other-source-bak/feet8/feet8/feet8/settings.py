#coding=utf-8
# Scrapy settings for feet8 project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
#将设置项按需要改动频率由大到小排列

BOT_NAME = 'feet8'

#为了快速启动,可仅设置spider所在目录,注释掉全局的'feet8.spiders'
SPIDER_MODULES = [
    #'feet8.spiders',
    #'feet8.spiders.bbs',
    #'feet8.spiders.news',
    #'feet8.spiders.weibo',
    #'feet8.spiders.company_info,
    'feet8.spiders.patent',
    # 'feet8.spiders.video'
    # 'feet8.spiders.video_zjcm'
]
#全局限制.
#开发限制,正式环境请在spider,setting里面覆盖设置这两项为None

#mongodb test
DATABASE = {
    'dbop': 'mongodb',
    'open_db_kwargs': {
        'url': 'mongodb://192.168.56.101:37017',
    },
    'db_name': 'feet8',
}

CLOSESPIDER_PAGECOUNT = 500
CLOSESPIDER_ITEMCOUNT = 100

#custom settings
DEBUG = True

NEWSPIDER_MODULE = 'feet8.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)"
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36'

ITEM_PIPELINES = [
    'feet8.pipelines.attachment.AttachmentPipeLine',
    'feet8.pipelines.save_item.SaveItemPipeline',
]
EXTENSIONS = {
    'feet8.extensions.db_manager.DbManager': 500
}
DOWNLOADER_MIDDLEWARES = {
}
SPIDER_MIDDLEWARES = {

}

#change default DEO order to BFO order,see doc/faq.
#改为使用广度优先爬取.
DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = 'scrapy.squeue.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeue.FifoMemoryQueue'

#cookie处理
COOKIES_ENABLED = False

#重定向
REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 20
REDIRECT_MAX_METAREFRESH_DELAY = 100

#重试.
RETRY_ENABLED = True
RETRY_TIMES = 1
RETRY_HTTP_CODES = [500, 503, 504, 400, 408]

#robot.txt
ROBOTSTXT_OBEY = False

#处理请求refer
REFERER_ENABLED = True

#请求头
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    #'Accept-Language': 'en',
}

#防重复爬取
# DUPEFILTER_CLASS = 'scrapy.dupefilter.RFPDupeFilter'


#日志
LOG_ENABLED = True
#日志级别.开发使用DEBUG,产品使用INFO提高性能
LOG_LEVEL = 'DEBUG'
LOG_FILE = None

DOWNLOADER_STATS = True #开启下载统计

#perfermance
RANDOMIZE_DOWNLOAD_DELAY = True #随机请求延迟
#调节CONCURRENT_ITEMS这里可以控制数据库读写压力.若process_item里有耗cpu计算,还可以控制cpu压力
CONCURRENT_ITEMS = 1024

NETWORK_SPEED = 'slow'
if NETWORK_SPEED == 'high':
    DOWNLOAD_TIMEOUT = 60*1   #访问超时
    CONCURRENT_REQUESTS = 128   #全局并发请求
    CONCURRENT_REQUESTS_PER_IP = 0
    CONCURRENT_REQUESTS_PER_DOMAIN = 128  #每域名并发请求数
    DOWNLOAD_DELAY = 0  #请求延迟
    AUTOTHROTTLE_ENABLED = True #自动调整请求频率- -.
elif NETWORK_SPEED == 'middle':
    DOWNLOAD_TIMEOUT = 60*3   #访问超时
    CONCURRENT_REQUESTS = 16   #全局并发请求
    CONCURRENT_REQUESTS_PER_IP = 0
    CONCURRENT_REQUESTS_PER_DOMAIN = 16  #每域名并发请求数
    DOWNLOAD_DELAY = 1  #请求延迟
    AUTOTHROTTLE_ENABLED = True #自动调整请求频率- -.
elif NETWORK_SPEED == 'slow':
    DOWNLOAD_TIMEOUT = 60*3   #访问超时
    CONCURRENT_REQUESTS = 4   #全局并发请求
    CONCURRENT_REQUESTS_PER_IP = 0
    CONCURRENT_REQUESTS_PER_DOMAIN = 1  #每域名并发请求数
    DOWNLOAD_DELAY = 1  #请求延迟
    AUTOTHROTTLE_ENABLED = False #自动调整请求频率- -.
elif NETWORK_SPEED == 'very slow':
    DOWNLOAD_TIMEOUT = 60*3   #访问超时
    CONCURRENT_REQUESTS = 1   #全局并发请求
    CONCURRENT_REQUESTS_PER_IP = 0
    CONCURRENT_REQUESTS_PER_DOMAIN = 1  #每域名并发请求数
    DOWNLOAD_DELAY = 10  #请求延迟
    AUTOTHROTTLE_ENABLED = False #自动调整请求频率- -.
else:
    #use scrapy default settings
    pass


# not used yet,发送邮件的功能
MAIL_FROM = ''
MAIL_HOST = ''
MAIL_PORT = ''
MAIL_USER = ''
MAIL_PASS = ''

#output
FEED_STORE_EMPTY = True

#telnet console
TELNETCONSOLE_ENABLED = False
WEBSERVICE_ENABLED = False

#wuya
COMMANDS_MODULE = 'feet8.commands'

#降低重试请求的优先级
RETRY_PRIORITY_ADJUST = 5



#custom
PRIORITIES = {
    'query': 100,
    'list': 50,
    'detail': 0,
}
PROXIES = [
    'http://proxyuser:Pa$$w0rd@112.11.119.231:33128',
    'http://proxyuser:Pa$$w0rd@112.11.119.232:33128',
    'http://proxyuser:Pa$$w0rd@112.11.119.233:33128',
    'http://proxyuser:Pa$$w0rd@112.11.119.234:33128',
    'http://proxyuser:Pa$$w0rd@112.11.119.235:33128',
    'http://proxyuser:Pa$$w0rd@112.11.119.236:33128',
]
FIREWALL_KEYWORDS = [
    '请求次数过多',
    '验证码',
    '机器人',
    '频繁'
]
#dupefilter
DUPEFILTER_CLASS = 'feet8.core.dupefilters.localmemory_dupefilter.LocalmemoryDupefilter'
DUPEFILTER_FILE = ''
DUPEFILTER_METHOD = 'cityhash64'
DUPEFILTER_HISTORY = 50000000
