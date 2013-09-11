"""
logerrmail extension sends an email when a spider finishes but with exceptioins

use ERRMAIL_LIST setting to enable
"""

from scrapy import signals
from scrapy.mail import MailSender
from scrapy.exceptions import NotConfigured

class LogErrMail(object):

    def __init__(self, stats, mail_list, mail):
        self.stats = stats
        self.mail_list = mail_list
        self.mail = mail

    @classmethod
    def from_crawler(cls, crawler):
        mail_list = crawler.settings.getlist("ERRMAIL_LIST")
        if not mail_list:
            raise NotConfigured
        mail = MailSender.from_settings(crawler.settings)
        o = cls(crawler.stats, mail_list, mail)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)

        return o

    def spider_closed(self, spider):
        spider_stats = self.stats.get_stats(spider)
        stats_str = ':'.join(spider_stats.keys())
        if stats_str.find('exception') or stats_str.find('Exceptions'):
            return self.mail.send("seem have see some exceptions")

