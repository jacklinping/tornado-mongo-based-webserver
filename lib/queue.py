#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
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

DEBUG = False

def debug(msg):
    if DEBUG:
        print msg

class Queue:

    def __init__(self):
        self.r = redis.Redis(config.Queue.host, config.Queue.port, config.Queue.db)

    def add(self, name, data):
        score = time.time()
        self.r.zadd(name, data, score)
        debug('Add %.1f, %s' % (score, data))

    def pop(self, name):
        min_score = 0
        max_score = time.time()

        result = self.r.zrangebyscore(
                name, min_score, max_score, start=0, num=1, withscores=False)
        if not result:
            return False

        if len(result) == 1:
            debug('Poped %s' % result[0])
            data = result[0]
            self.r.zrem(name, result[0])
            return data
        else:
            return False


