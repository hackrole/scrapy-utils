#!/usr/bin/env python
#coding=utf-8

import gevent
from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool

import db
import time
import sched
import config
from utils import handle

gpool = Pool(config.GPOOLSIZE)


def work():
    jobs = db.get_jobs()
    print jobs
    gpool.map(handle, jobs)


def cycle_run(interval):
    s.enter(interval, 0, cycle_run, (interval,))
    work()


if __name__ == '__main__':
    interval = config.INTERVAL
    s = sched.scheduler(time.time, gevent.sleep)
    s.enter(interval, 0, cycle_run, (interval, ))
    s.run()
