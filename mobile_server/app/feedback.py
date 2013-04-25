#-*- coding: utf-8 -*-

from db import mongo
import tornado
from lib.memsession import MemcacheStore
from lib.session import Session
import datetime
from libs import BaseHandler
import pymongo
from pymongo import Connection

class FeedbackHandler(BaseHandler):
    def get(self):
        self.render("feedback.html",context=self.context)

class FeedbackSaveHandler(BaseHandler):
    def get(self):
        comment = self.get_argument("comment", default=None)
        email = self.get_argument("email", default=None)
        try:
            ua = self.request.headers['User-Agent']
        except:
            ua = ''

        if not comment: return

        post = {
                "feedContent": comment,
                "email": email,
                "ua": ua,
                "datetime":datetime.datetime.now()
                }
        mongo.feed.insert(post)
