#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import redis
import tornado

from lib.memsession import MemcacheStore
from lib.session import Session
from lib.cache import Cache
from lib.queue import Queue
from conf import config
from db import live_mongo,mongo,theme_mongo

class BaseHandler(tornado.web.RequestHandler):

    def initialize(self):
        self.db = mongo
        self.search_cache = Cache(master=False, db=config.Cache.searchdb)
        self.hot_image_cache = Cache(master=False, db=config.Cache.imagedb)
        self.queue = Queue()

        self.session = Session(self, MemcacheStore(),
                initializer = {
                    'nickname': None,
                    'uid': None,
                    'avatar': None,
                    'email': None,
                    'super': False,
                    'channel': None,
                    'login': False,
                    'net': None,
                    'reso': None,
                    'height': 0,
                    'width': 0,
                    'show_msg':None,
                    'hd':True
                    }
                )
        self.session.processor(self)
        self.context = {
                'se': self.session,
                'static_server': config.Server.static_server,
                'cdn':config.CDN.mhost,
                }

    def get_current_user(self):
        try:
            return self.session.uid
        except:
            return None

    def split_page(self, length, offset, limit):
        if offset > 0:
            if offset <= limit:
                front = 0
            else:
                front = (offset - limit) /limit
        else:
            front = None

        if offset+limit < length:
            end = (offset+limit)/limit
        else:
            end = None

        page = (offset+limit)/limit
        i = length / limit
        j = length % limit
        total = i if j == 0 else i+1

        return front, end, page, total

    def get_error_html(self,status_code, **kwargs):
        return self.render_string("error.html", error_code=status_code)

    def notfound(self):
        self.render("notfound.html")

    def flash(self,msg):
        self.session.show_msg = None
        self.session.msg = msg
