#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
from db import live_mongo,mongo
import tornado
from lib.memsession import MemcacheStore
from lib.session import Session

class BaseHandler(tornado.web.RequestHandler):

    debug = True

    def debug(self, message=''):
        if self.debug:
            import sys

            call_func_name = sys._getframe(1).f_code.co_name
            class_name = self.__class__.__name__

            print '[ %s:%s ] %s' % (class_name, call_func_name, message)
        else:
            pass

    def initialize(self):
        self.db = mongo
        self.message = None

        self.session = Session(self,MemcacheStore(),
                    initializer = {
                        'nickname': None,
                        'uid': None,
                        'email': None,
                        'super': False,
                        'artist': False,
                        }
                    )
        self.session.processor(self)

    def prepare(self):
        if self.session.uid and not self.session.super:
            raise tornado.web.HTTPError(404)


    def get_current_user(self):
        try:
            return self.session.uid
        except:
            return None


    def get_error_html(self,status_code, **kwargs):
        return self.render_string(
                "error.html",
                error_code=status_code
                )

    def split_page(self, length, offset, limit):
        if offset > 0:
            if offset <= limit:
                front = 0
            else:
                front = offset - limit
        else:
            front = None

        if offset + limit < length:
            end = offset + limit
        else:
            end = None

        tail = (length / limit) * limit
        if tail < 0: tail = 0

        page = (offset + limit) / limit
        i = length / limit
        j = length % limit
        total = i if j == 0 else i+1

        return front, end, tail, "%d/%d" % (page, total)
