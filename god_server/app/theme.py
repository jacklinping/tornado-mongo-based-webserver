#!/usr/bin/env python
# -*- coding: utf-8 -*-

from db import theme_mongo

import tornado
from pymongo import DESCENDING, ASCENDING
from bson import objectid
import urllib

from libs import BaseHandler
import datetime

def save_thumb(fileValue):
    if not fileValue:
        return None
    thumbid = theme_mongo.filefs.put(fileValue['body'])
    return thumbid

class HomeHandler(BaseHandler):
    def get(self, cateid=None):
        try:
            cid = objectid.ObjectId(cateid)
        except:
            cid = None

        categorys = theme_mongo.category.find()

        if cid:
            current_cate = theme_mongo.category.find_one({'_id': cid})
        else:
            try:
                current_cate = categorys[0]
            except IndexError:
                current_cate = None

        apks = []
        if current_cate:
            apks = theme_mongo.apk.find({'cid': cid})

        self.render("theme.html",
                current_cate = current_cate,
                context=self.context,
                categorys=categorys,
                apklist=apks,
                type=2,
                )

class ListHandler(BaseHandler):
    def get(self,cateid):
        try:
            cid = objectid.ObjectId(cateid)
        except:
            raise tornado.web.HTTPError(404)

        category = theme_mongo.category.find_one({
            '_id': cid
            })
        if not category:
            raise tornado.web.HTTPError(404)
        apks = theme_mongo.apk.find({'cid': cid})
        self.render("list.html",
                apklist=apks,
                category=category,
                type=2,
                )


class CreateHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        print 'create handler'
        self.render("create.html",
                context=self.context,
                message='',
                )

    @tornado.web.authenticated
    def post(self):
        print 'post create handler'
        cname = self.get_argument("name",default='')
        rname = self.get_argument("rname", default='')
        print cname
        thumbView = None
        if self.request.files:
            thumbView = self.request.files['thumb'][0]

        thumbid = save_thumb(thumbView)

        name = cname.strip()
        alertMessage = ''
        if name == '':
            alertMessage='名字不能为空'
            self.render("create.html",
                    context=self.context,
                    message=alertMessage,
                    )
            return
        if theme_mongo.category.find_one({'name': name}):
            alertMessage='分类已存在'
            self.render("create.html",
                    context=self.context,
                    message=alertMessage,
                    )
            return

        cateid = theme_mongo.category.insert({
            'name': name,
            'uid': self.session.uid,
            'rname': rname,
            'thumbid': thumbid,
            'atime': datetime.datetime.now()
            })
        print str(cateid)
        self.redirect("/themecate/list/%s" % str(cateid))



class EditHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,cateid):
        print 'edit handler',cateid
        try:
            cid = objectid.ObjectId(cateid)
        except:
            raise tornado.web.HTTPError(404)
        cate = theme_mongo.category.find_one({'_id':cid})
        if not cate:
            raise tornado.web.HTTPError(404)

        self.render("editCate.html",
                context=self.context,
                category=cate,
                message='',
                )

    @tornado.web.authenticated
    def post(self,caid):
        print 'edit post handler'
        cname = self.get_argument("name",default='')
        rname = self.get_argument("rname",default='')
        cid = self.get_argument("cateid",default=None)
        thumbView, iconView= None,None
        if self.request.files:
            thumbView = self.request.files['thumb'][0]
            iconView = self.request.files['icon'][0]

        name = cname.strip()

        try:
            cateid = objectid.ObjectId(cid)
            cate = theme_mongo.category.find_one({'_id':cateid})
            if not cate:
                raise tornado.web.HTTPError(404)
        except:
            raise tornado.web.HTTPError(404)

        if name=='':
            message = '分类名称不能为空'
            return self.render("editCate.html",
                    category=cate,
                    message=message,
                    )
        elif theme_mongo.category.find_one({'name':name}) and cate['name'] != name:
            message = '分类已存在'
            return self.render("editCate.html",
                    category=cate,
                    message=message,
                    )

        thumbid = save_thumb(thumbView)
        iconid = save_thumb(iconView)

        if thumbid and iconid:
            theme_mongo.category.update(
                {'_id':cateid},
                {'$set':{
                    'name':name,
                    'uid':self.session.uid,
                    'rname':rname,
                    'thumbid':thumbid,
                    'iconid': iconid,
                    'ctime':datetime.datetime.now()
                    }
                })
        elif thumbid:
            theme_mongo.category.update(
                {'_id':cateid},
                {'$set':{
                    'name':name,
                    'uid':self.session.uid,
                    'rname':rname,
                    'thumbid':thumbid,
                    'ctime':datetime.datetime.now()
                    }
                })
        elif iconid:
            theme_mongo.category.update(
                {'_id':cateid},
                {'$set':{
                    'name':name,
                    'uid':self.session.uid,
                    'rname':rname,
                    'iconid': iconid,
                    'ctime':datetime.datetime.now()
                    }
                })
        else:
            theme_mongo.category.update(
                {'_id':cateid},
                {'$set':{
                    'name':name,
                    'uid':self.session.uid,
                    'rname':rname,
                    'ctime':datetime.datetime.now()
                    }
                })
        self.redirect("/")

