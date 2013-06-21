# for mail
MAIL_FROM = "daipeng@ebuinfo.com"
MAIL_HOST = "smtp.exmail.qq.com"
MAIL_USER = "daipeng@ebuinfo.com"
MAIL_PASS = "123456"
#stats mail
STATSMAILER_RCPTS = ['daipeng@ebuinfo.com',]
ERRMAIL_LIST = ['daipeng@ebuinfo.com',]

# extension
EXTENSIONS = {
    "scrapy.contrib.statsmailer.StatsMailer": 500,
    #"video.extensions.logerrmail.LogErrMail": 500,
}

# download middlewares
DOWNLOAD_MIDDLEWARES = {
    'mey.middlewares.',
}
