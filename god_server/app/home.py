#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado
from bson import objectid
from pymongo import DESCENDING, ASCENDING
from libs import BaseHandler
from db import live_mongo,theme_mongo


class HomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):

        categorys = live_mongo.category.find()

        self.render("home.html",
                categorys=categorys,
                )

class DownloadHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,thumbid):
        ctype = self.get_argument('type',default=1)
        ctype = int(ctype)
        img = None
        try:
            tid = objectid.ObjectId(thumbid)
            if ctype==1:
                img = live_mongo.filefs.get(tid).read()
            else:
                img = theme_mongo.filefs.get(tid).read()
            if not img:
                raise
        except:
            raise tornado.web.HTTPError(404)

        self.set_header('Content-Type','image/jpg')
        self.write(img)
