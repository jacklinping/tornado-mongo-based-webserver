#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado
from bson import objectid
from pymongo import DESCENDING, ASCENDING
from libs import BaseHandler
from db import mongo
import json
import datetime
import os
import hashlib
import urllib
import tornado.web


class HomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        messages = mongo.messagedeliver.find().sort('atime', DESCENDING)
        self.render("messagehome.html",
                messages=messages,
                )

class CreateHandler(BaseHandler):
    def post(self):
        title = self.get_argument('title', default=None)
        content = self.get_argument('content', default=None)
        link = self.get_argument('link', default=None)
        datefrom = self.get_argument('datefrom', default=None)
        dateto = self.get_argument('dateto', default=None)
        time = self.get_argument('time', default=None)

        if not datefrom:
            datefrom = None
        if not dateto:
            dateto = None
        if not time:
            time = None
        mongo.messagedeliver.insert({'title':title,'content':content,'link':link,'datefrom':datefrom,'dateto':dateto,'time':time,'atime':datetime.datetime.now()})
        self.redirect("/messagedeliver/home")

    @tornado.web.authenticated
    def get(self):
        self.render("messages_create.html",
                )

class EditHandler(BaseHandler):
    def post(self):
        mid = self.get_argument('mid', default=None)
        title = self.get_argument('title', default=None)
        content = self.get_argument('content', default=None)
        link = self.get_argument('link', default=None)
        datefrom = self.get_argument('datefrom', default=None)
        dateto = self.get_argument('dateto', default=None)
        time = self.get_argument('time', default=None)

        message = mongo.messagedeliver.find_one({'_id':objectid.ObjectId(mid)})
        print message
        if message:
            if not datefrom:
                datefrom = None
            if not dateto:
                dateto = None
            if not time:
                time = None
            mongo.messagedeliver.update(
                    {'_id':objectid.ObjectId(mid)},
                    { '$set':{'title':title,'content':content,'link':link,'datefrom':datefrom,'dateto':dateto,'time':time,'atime':datetime.datetime.now()}})
            self.redirect("/messagedeliver/home")
        else:
            raise tornado.web.HTTPError(404)

    @tornado.web.authenticated
    def get(self):
        mid = self.get_argument('mid', default=None)
        message = mongo.messagedeliver.find_one({'_id':objectid.ObjectId(mid)})
        if message:
            self.render("messages_edit.html",
                    message = message,
                    )
        else:
            raise tornado.web.HTTPError(404)

class DeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        mid = self.get_argument('mid', default=None)
        message = mongo.messagedeliver.find_one({'_id':objectid.ObjectId(mid)})
        if message:
            mongo.messagedeliver.remove({'_id':objectid.ObjectId(mid)})
        self.redirect("/messagedeliver/home")

