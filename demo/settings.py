
# Scrapy settings for lunwen project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
import socket

BOT_NAME = 'lunwen'

SPIDER_MODULES = ['lunwen.spiders']
NEWSPIDER_MODULE = 'lunwen.spiders'

# cookie
#COOKIES_ENABLED = False
#COOKIES_DEBUG = True

# others
REFERER_ENABLED = True
ROBOTSTXT_OBEY = False

# download middleware
DOWNLOADER_MIDDLEWARES = {
        'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': '510',
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)'

host_ip = socket.gethostbyname(socket.gethostname())

if host_ip == "127.0.1.1":
    DEBUG = True
else:
    DEBUG = False

# load the right settings file
if DEBUG:
    from settings_dev import *
else:
    from settings_prod import *

