#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado
from bson import objectid
from pymongo import DESCENDING, ASCENDING
import urllib

from libs import BaseHandler
from db import live_mongo
import datetime

def save_thumb(fileValue):
    if not fileValue:
        return None
    thumbid = live_mongo.filefs.put(fileValue['body'])
    return thumbid

class HomeHandler(BaseHandler):
    limit = 20

    @tornado.web.authenticated
    def get(self, cateid=None, offset=None):

        self.debug('cateid is %s, offset is %s' % (cateid, offset))

        cid = None
        try:
            if cateid:
                cid = objectid.ObjectId(cateid)
        except:
            cid = None

        try:
            offset = int(offset)
        except:
            offset = 0

        if cid:
            current_cate = live_mongo.category.find_one({'_id': cid})
        else:
            current_cate = live_mongo.category.find_one()

        apks = []
        if current_cate:
            apks = live_mongo.apk.find({'cid': current_cate['_id']}).skip(offset).limit(self.limit)

        categorys = live_mongo.category.find()

        length = apks.count()

        front, end, tail, page = self.split_page(length, offset, self.limit)

        self.render("live.html",
                current_cate = current_cate,
                categorys=categorys,
                apklist=apks,
                front=front,
                end=end,
                tail=tail,
                page=page,
                type=1,
                )


class CreateHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("create.html",
                )

    @tornado.web.authenticated
    def post(self):
        cname = self.get_argument("name",default='')
        rname = self.get_argument("rname", default='')
        thumbView,iconView = None,None
        if self.request.files:
            thumbView = self.request.files['thumb'][0]

        thumbid = save_thumb(thumbView)

        name = cname.strip()
        alertMessage = ''
        if not thumbid:
            self.message = '分类图不能为空'
            return self.render("create.html")

        if name == '':
            self.message = '名字不能为空'
            return self.render("create.html")

        if live_mongo.category.find_one({'name': name}):
            self.message = '分类已存在'
            return self.render("create.html")

        cateid = live_mongo.category.insert({
            'name': name,
            'uid': self.session.uid,
            'rname': rname,
            'thumbid': thumbid,
            'atime': datetime.datetime.now()
            })

        self.message = "创建成功"
        self.redirect("/live/home/%s/0" % str(cateid))


class EditHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,cateid):
        try:
            cid = objectid.ObjectId(cateid)
        except:
            raise tornado.web.HTTPError(404)
        cate = live_mongo.category.find_one({'_id':cid})
        if not cate:
            raise tornado.web.HTTPError(404)

        self.render("editCate.html",
                category=cate,
                )
    
    @tornado.web.authenticated
    def post(self,caid):
        cname = self.get_argument("name",default='')
        rname = self.get_argument("rname", default='')
        cid = self.get_argument("cateid",default=None)
        thumbView= None
        if self.request.files:
            thumbView = self.request.files['thumb'][0]

        thumbid = save_thumb(thumbView)
        name = cname.strip()

        try:
            cateid = objectid.ObjectId(cid)
            cate = live_mongo.category.find_one({'_id':cateid})
            if not cate:
                raise tornado.web.HTTPError(404)
        except:
            raise tornado.web.HTTPError(404)

        if name=='':
            self.message = '分类名称不能为空'
            return self.render("editCate.html",
                    category=cate,
                    )
        elif live_mongo.category.find_one({'name':name}) and cate['name'] != name:
            self.message = '分类已存在'
            return self.render("editCate.html",
                    category=cate,
                    )

        if thumbid:
            live_mongo.category.update(
                {'_id':cateid},
                {'$set':{
                    'name':name,
                    'rname':rname,
                    'thumbid':thumbid,
                    'uid':self.session.uid,
                    'ctime':datetime.datetime.now()
                    }
                 })
        else:
            live_mongo.category.update(
                {'_id':cateid},
                {'$set':{
                    'name':name,
                    'rname':rname,
                    'uid':self.session.uid,
                    'ctime':datetime.datetime.now()
                    }
                 })

        self.message = "修改成功"
        self.redirect("/live/home/%s/0" % str(cateid))

