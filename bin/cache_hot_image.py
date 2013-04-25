#!/usr/bin/python
# -*- coding: utf-8 -*-

import traceback
from pymongo import DESCENDING, ASCENDING
from redis import Redis
from bson import objectid 

import os
import sys
import json
import datetime
sys.path += [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]
from db import mongo
from conf import config
from lib.cache import Cache

class HotImage:

    def __init__(self):
        self.maximg = 5000
        self.name = config.Cache.hot_image_cache
        self.c = Cache(master=True, db=config.Cache.imagedb)

    def _get_hot_images(self, days):

        start = datetime.datetime.now() - datetime.timedelta(
                days = days
                )
        settinglog = mongo.setting_log.find({
            'atime': {'$gt': start}
            })

        hot = {}
        for i in settinglog:
            if not hot.has_key(i['imgid']):
                hot[i['imgid']] = 1
            else:
                hot[i['imgid']] += 1

        return list(sorted(hot.items(), key=lambda x: x[1]))

    def cache_hot_images(self, days):
        from lib.encoder import MongoEncoder

        self.delete_cache()

        imgs = [i[0] for i in self._get_hot_images(days)]
        imgs.reverse()
        print 'hot image size', len(imgs)
        for i in imgs:
            try:
                img = mongo.image.find_one({'_id': objectid.ObjectId(i)})
                if img:
                    self.c.rpush(self.name, json.dumps(
                        img, cls=MongoEncoder)
                        )
            except:
                raise
                continue

    def delete_cache(self):
        print 'remove cache', self.name
        self.c.remove(self.name)

    def get(self, num):
        return self.c.find_list(self.name, 0, num)
        
            
def main():

    from optparse import OptionParser

    usage = 'usage: %prog [options] arg'
    parser = OptionParser(usage)

    parser.add_option('-n', '--day', type="int", dest="day", help="how many days log")
    parser.add_option('-g', '--get', type="int", dest="get")
    parser.add_option('-d', '--delete', action="store_true", dest="delete")

    (options, args) = parser.parse_args()

    h = HotImage()
    if options.day:
        h.cache_hot_images(options.day)
    elif options.delete:
        h.delete_cache()
    elif options.get:
        print h.get(options.get)

if __name__ == '__main__':
    main()
     
