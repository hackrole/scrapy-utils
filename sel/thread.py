#coding=utf8
import Queue
import threading
import time
import lunwen
import random
from selenium import webdriver
from selenium.webdriver.common.proxy import *

queue = Queue.Queue()

class ThreadUrl(threading.Thread):
    def __init__(self, queue, pro):
        threading.Thread.__init__(self)
        self.queue = queue
        self.pro = pro

    def run(self):
        while True:
            kw = self.queue.get()
            print kw, self.pro
            lunwen.main(kw, self.pro)
            time.sleep(300)
            self.queue.task_done()
        return

def main():
    words = lunwen.get_keyword()
    kw = [w for word in words for w in word['keyword'].split('|')]
    kw.append(u'cad')
    kw.append(u'数字化制造')
    for k in kw:
        queue.put(k)

    pro = open('proxy_use.txt').readlines()
    text = [i.strip('\n ') for i in pro]
    proes = []
    for i in text:
        proes.append(i.split('\t')[0])

    for i in range(2):
        #p = pro[random.randint(0, len(pro)-1)]
        #p = i % len(pro)
        p = proes[i]
        t = ThreadUrl(queue, proes[i])
        t.setDaemon(True)
        t.start()
        time.sleep(10)

    queue.join()

if __name__ == "__main__":
    start = time.time()
    main()
    print "time: %s" % (time.time() - start)

