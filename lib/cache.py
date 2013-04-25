#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import redis
import os,sys
root_path = [os.path.dirname( #live-server
    os.path.abspath(__file__)
    )]
sys.path += root_path

from conf import config
from db import mongo
from encoder import MongoEncoder


class Cache:
    
    def __init__(self, master=True, db=config.Cache.db):
        if master:
            self.r = redis.Redis(host=config.Cache.master, port=config.Cache.port, db=db)
        else:
            _host = self.__get_hashed_host()
            self.r = redis.Redis(host=_host, port=config.Cache.port, db=db)

    def __get_hashed_host(self):
            import socket
            hostname = socket.gethostname()

            idx = hash(hostname) % len(config.Cache.slaves)
            return config.Cache.slaves[idx]


#     def save_search_list(self, name, _list):
#         for i in list(set(_list)):
#             img = mongo.image.find_one({'_id': i})
#             if img:
#                 self.r.rpush(name, json.dumps(img, cls=MongoEncoder))

#     def save_list(self, name, _list):
#         for i in _list:
#             img = mongo.image.find_one({'_id': i})
#             if img:
#                 self.r.rpush(name, json.dumps(img, cls=MongoEncoder))

    def find_list(self, name, skip, limit):
        start = skip
        end = skip + limit

        return self.r.lrange(name, start, end), self.r.llen(name)

    def find_one(self, name, skip):
        ret = self.r.lindex(name, skip)
        return ret

    def llen(self, name):
        return self.r.llen(name)

    def rpush(self, name, value):
        return self.r.rpush(name, value)

    def flush(self):
        return self.r.flushdb()

    def remove(self, name):
        return self.r.delete(name)
