#-*- encoding: utf-8 -*-

import tornado
from bson import objectid
from pymongo import DESCENDING, ASCENDING
import urllib
import datetime
from libs import BaseHandler
from db import mongo
import MailSys
from conf import config
#import libs as lb

class LoginHandler(BaseHandler):
    def get(self):
        referer = self.get_argument('referer',default='/')

        self.render("login.html",
                referer=referer,
                )

    def post(self):
        email = self.get_argument('email',default=None)
        passwd = self.get_argument('password',default=None)
        referer = self.get_argument('next',default='/')

        if not email or not passwd:
            self.message='用户名或密码不正确'
            return self.render("login.html",
                    referer=referer,
                    )

        user = mongo.user.find_one({'email':email,'passwd':passwd})
        if not user:
            self.message='帐号或密码错误'
            return self.render("login.html",
                    referer=referer,
                    )

        if not user['super']:
            self.message="权限错误"
            return self.render("login.html",
                    referer=referer,
                    )

        mongo.user.update({'email':email},
                {'$set': {
                    'logined': True,
                    'lastlogin': datetime.datetime.now()
                    }})

        self.session.uid = user['_id']
        self.session.nickname = user['nickname']
        self.session.email = user['email']
        self.session.super = user['super']
        self.session.artist = user['artist']

        self.redirect(referer)

class LogoutHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        mongo.user.update(
                {'_id': self.session.uid},
                {'$set':{'logined': False,}}
               )

        self.session.clean()
        self.redirect("/")


