#! -*- coding: utf-8 -*-

import traceback
from pymongo import DESCENDING, ASCENDING
from redis import Redis
from bson import objectid 
import os, sys, json, time, threading

sys.path += [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]
from db import mongo
from conf import config
from lib import utils, cache, queue, oset

lock = threading.Lock()

cache_lock = threading.Lock()

"""
handlers
"""
def send_mail(task, num):

    task = json.loads(task)
    email = task['email']
    code = task['code']

    print 'Slave [ %d ] send email to %s' % (num, task['email'])

    utils.sendmail(config.Mail._from,
            email,
            config.Mail._reset_subject,
            config.Mail._reset_message % str(code)
            )

def __get_all_image_by_name(words):
    import re
    key = ' '.join(words.split())
    key = key.replace(' ','|')

    reg = ''
    try:
        reg = re.compile(key, re.IGNORECASE)
    except:
        return []

    taglist = mongo.tag.find({
        'name': reg},limit=100).sort('rank',DESCENDING)

    names = [i['name'] for i in taglist]
    
    imgids = list(oset.Oset([i['imgid'] for i in mongo.img2tag.find({'name': {'$in': names}}).sort('atime', DESCENDING)]))
    return imgids

def cache_search(name, num):
    from lib.encoder import MongoEncoder

    c = cache.Cache(master=True, db=config.Cache.searchdb)

    if c.llen(name) > 0:
        return

    print 'Slave [ %d ] genrate search cache %s' % (num, name)

    imgids = __get_all_image_by_name(name)

    for i in imgids:
        try:
            _id = objectid.ObjectId(i)
            img = mongo.image.find_one({'_id': _id})
            if img:
                c.rpush(name, json.dumps(
                    img, cls=MongoEncoder)
                    )
        except:
            raise
            continue
    print 'Slave [ %d ] generate %s finish...' % (num, name)

class SlaveAlpha(threading.Thread):
    def __init__(self, num):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.num = num

        print 'Slave [ %d ] start' % num

    def run(self):
        while True:
            time.sleep(0.5)
            try:
                for i in config.Queue.queue:
                    with lock: task = self.queue.pop(i)
                    if not task: 
                        continue

                    exec('%s(task, self.num)' % i)
            except:
                print 'Slave [ %d ] error occur: %s' % (self.num, traceback.format_exc())


def main():
    slaves = []
    
    for i in range(8):
        s = SlaveAlpha(i)
        slaves.append(s)
        s.start()
        
    for i in slaves:
        i.join()

if __name__ == '__main__':
    main()

