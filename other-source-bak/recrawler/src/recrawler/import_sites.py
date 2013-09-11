#!/usr/bin/env python
#coding=utf-8

import config
import cityhash
import PySQLPool
import tldextracter

connection = PySQLPool.getNewConnection(
    username=config.DB_USER,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
    db=config.DB_DB,
    charset=config.DB_CHARSET)


def init():
    '''
CREATE TABLE `news_sites` (
`id` INT UNSIGNED PRIMARY KEY NOT NULL AUTO_INCREMENT,
`domainhash` BIGINT UNSIGNED NOT NULL DEFAULT 0,
`language` TINYINT UNSIGNED DEFAULT 1 NOT NULL,
`name` VARCHAR(128) NOT NULL DEFAULT '',
`domain` VARCHAR(100) NOT NULL DEFAULT '',
`url` VARCHAR(512) NOT NULL DEFAULT ''
) Engine=INNoDB DEFAULT CHARSET=utf8;
    '''
    pass


def insert_site(name, language, url):

    if isinstance(url, unicode):
        try:
            url = url.strip().encode('utf8')
        except Exception, e:
            print e
            pass
    rootdomain = tldextracter.extract_rootdomain(url)
    domainhash = cityhash.CityHash64(rootdomain)
    query = PySQLPool.getNewQuery(connection)
    query.Query('''select domainhash from news_sites where domainhash = %s;''',
                domainhash)
    if query.record:
        return False
    else:
        query.Query('insert into news_sites(domainhash, language, name, '
                    'domain, url) values(%s, %s, %s, %s, %s);',
                    (domainhash, language, name, rootdomain, url))
        query.Pool.Commit()
        return True


if __name__ == '__main__':
    from rulers import RULERS
    for ruler in RULERS:
        site = RULERS[ruler]
        name = site["name"]
        url = site["url"]
        language = site["language"]
        print name, url, language
        print insert_site(name, language, url)
