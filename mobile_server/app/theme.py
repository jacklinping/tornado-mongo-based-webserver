#!/usr/bin/env python 
#-*- coding:utf-8 -*-

import tornado
import json
import base64
import re
from libs import BaseHandler
from db import theme_mongo
from pymongo import DESCENDING, ASCENDING
from bson import objectid
import urllib

class CategoryHandler(BaseHandler):
    def get(self):
        cates = theme_mongo.category.find()
        if not cates:
            raise tornado.web.HTTPError(404)
        self.render("theme_category.html",
                context=self.context,
                cates=cates,
                )


class ListHandler(BaseHandler):
    limit = 9
    def get(self):
        cateid = self.get_argument("cateid", default=None)
        skip = self.get_argument("skip", default=None)
        order = self.get_argument("order",default=None)
        if not skip:
            skip = 0
        if not order:
            order = "newest"
        try:
            cid = objectid.ObjectId(cateid)
        except:
            raise tornaod.web.HTTPError(404)

        cname = ''
        cate = theme_mongo.category.find_one({'_id':cid})
        if cate:
            cname = cate['name']


        self.render("theme_list.html",
                context=self.context,
        #        apklist=apklist,
                cname=cname,
                cateid=cid,
                skip=skip,
                order=order,
        #        front=front,
        #        end=end,
        #        page=page,
        #        total=total,
                )

class MoreListHandler(BaseHandler):
    limit = 9 
    def get(self):
        cateid = self.get_argument("cateid", default=None)
        skip = self.get_argument("skip", default=0)
        order = self.get_argument("order",default=None)
        if not skip: skip = 0
        skip = int(skip)
        if not order:
            order = 'newest'
        try:
            cid = objectid.ObjectId(cateid)
        except:
            raise tornado.web.HTTPError(404)

        themes = []
        if order == 'newest':
            themelist = theme_mongo.apk.find({'cid':cid}, skip=skip, limit=self.limit).sort('atime',DESCENDING)
        else:
            themelist = theme_mongo.apk.find({'cid':cid}, skip=skip, limit=self.limit).sort('rank',DESCENDING)

        for i in themelist:
            themes.append({
                    '_id': str(i['_id']),
                    'name': i['name'],
            #        'pname': i['package_name'],
            #        'pversoin':i['package_version'],
            #        'psize':i['package_size'],
            #        'picon':i['package_icon'],
                    'cid': str(i['cid']),
           #         'uid': str(i['uid']),
                    'thumbid': str(i['thumbid'][0]),
           #         'savepath': i['savepath'],
           #         'descr': i['descr'],
           #         'atime': i['atime'],
                })

        self._buffer = json.dumps({'code':0, 'resp':themes})
        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)
        self.write(self._buffer)

class DetailHandler(BaseHandler):
    def get(self,apkid):
        try:
            pid = objectid.ObjectId(apkid)
            apk = theme_mongo.apk.find_one({'_id':pid})
            if not apk:
                raise
        except:
            raise tornado.web.HTTPError(404)

        skip = self.get_argument("skip",default=None)
        if not skip: skip = 0
        order = self.get_argument("order",default=None)
        if not order: order = 'newest'
        skip=int(skip)
        cate = theme_mongo.category.find_one({'_id':apk['cid']})
        cname = ''
        if cate:
            cname = cate['name']
        tags = theme_mongo.theme2tag.find({'apkid':pid})
        if order == 'newest':
            listcount = theme_mongo.apk.find({'cid':apk['cid']}, skip=skip, limit=3).sort('atime',DESCENDING).count()
        else:
            listcount = theme_mongo.apk.find({'cid':apk['cid']}, skip=skip, limit=3).sort('rank',DESCENDING).count()
        front = skip-1
        end = skip+1
        if end>=listcount:
            end=-1

        isfav =-1 
        if self.session.uid:
            pri=theme_mongo.private.find_one({'uid':self.session.uid,'apkid':apk['_id']})
            if pri:
                isfav=1
            else:
                isfav=0
        referer = self.request.uri
       # referer = base64.encodestring(referer)
        referer = urllib.quote(referer)
        self.render("theme_detail.html",
                context=self.context,
                cname=cname,
                apk=apk,
                favstate=isfav,
                tags=tags,
                referer=referer,
                order=order,
                skip=skip,
                front=front,
                end=end,
                )

class OrderHandler(BaseHandler):
    def get(self):
        order = self.get_argument("order",default=None)
        skip = self.get_argument("skip",default=None)
        cateid = self.get_argument("cateid",default=None)
        if not order or not skip or not cateid:
            raise tornado.web.HTTPError(500)
        skip = int(skip)
        if skip<0: skip=0
        try:
            cid = objectid.ObjectId(cateid)
            cate = theme_mongo.category.find_one({'_id':cid})
            if not cate:
                raise
        except:
            raise tornado.web.HTTPError(500)
        cname = cate['name']

        if order == 'newest':
            apks = theme_mongo.apk.find({'cid':cid}, skip=skip, limit=2).sort('atime',DESCENDING)
        else:
            apks = theme_mongo.apk.find({'cid':cid}, skip=skip, limit=2).sort('rank',DESCENDING)
        front = skip-1
        if apks.count()>skip:
            apk=apks[0]
        end = skip+1
        if end>=apks.count():
            end = -1
        tags = []
        if apk:
            tags = theme_mongo.theme2tag.find({'apkid':apk['_id']})
        referer = self.request.uri
        #referer = base64.encodestring(referer)
        referer = urllib.quote(referer)
        isfav = -1
        if self.session.uid:
            pri=theme_mongo.private.find_one({'uid':self.session.uid,'apkid':apk['_id']})
            if pri:
                isfav=1
            else:
                isfav=0

        self.render("theme_detail.html",
                context=self.context,
                cname=cname,
                favstate=isfav,
                apk=apk,
                referer=referer,
                tags=tags,
                order=order,
                skip=skip,
                front=front,
                end=end,
               )

class FavorHandler(BaseHandler):
    def get(self):
        skip = self.get_argument("skip",default=None)
        userid = self.get_argument("userid",default=None)
        if not skip or not userid:
            raise tornado.web.HTTPError(404)

        skip = int(skip)
        if skip<0: skip=0
        try:
            uid = objectid.ObjectId(userid)
        except:
            return self.notfound()

        privates = theme_mongo.private.find({'uid':uid},skip=skip,limit=2).sort('atime',DESCENDING)

        #apks = theme_mongo.apk.find({'uid':uid}, skip=skip, limit=2).sort('atime',DESCENDING)

        front = skip-1
        if privates.count()>skip:
            tmp = privates[0]
            if tmp:
                apk = theme_mongo.apk.find_one({'_id':tmp['apkid']})
        elif privates.count()>0:
            skip = 0
            front = skip-1
            privates = theme_mongo.private.find({'uid':uid},skip=skip,limit=2).sort('atime',DESCENDING)
            tmp=privates[0]
            if tmp:
                apk = theme_mongo.apk.find_one({'_id':tmp['apkid']})
        else:
            return self.redirect('/themefavor/%s' % userid)
        end = skip+1
        if end>=privates.count():
            end = -1
        tags = []
        if apk:
            tags = theme_mongo.theme2tag.find({'apkid':apk['_id']})
        referer = self.request.uri
       # referer = base64.encodestring(referer)
        referer = urllib.quote(referer)
        self.render("favortheme_detail.html",
                context=self.context,
                userid=userid,
                apk=apk,
                referer=referer,
                tags=tags,
                skip=skip,
                front=front,
                end=end,
               )

class ExplorerHandler(BaseHandler):
    def get(self):
        skip = self.get_argument("skip",default=None)
        cateid = self.get_argument("cateid",default=None)
        if not skip or not cateid:
            raise tornado.web.HTTPError(500)
        skip = int(skip)
        if skip<0: skip=0
        try:
            cid = objectid.ObjectId(cateid)
            cate = theme_mongo.category.find_one({'_id':cid})
            if not cate:
                raise
        except:
            raise tornado.web.HTTPError(500)
        cname = cate['name']

        apks = theme_mongo.apk.find({'cid':cid}, skip=skip, limit=2)
        front = skip-1
        if apks.count()>skip:
            apk=apks[0]
        end = skip+1
        if end>=apks.count():
            end = -1
        tags = []
        if apk:
            tags = theme_mongo.theme2tag.find({'apkid':apk['_id']})

        referer = self.request.uri
        #referer = base64.encodestring(referer)
        referer = urllib.quote(referer)
        isfav =-1
        if self.session.uid:
            pri=theme_mongo.private.find_one({'uid':self.session.uid,'apkid':apk['_id']})
            if pri:
                isfav=1
            else:
                isfav=0

        self.render("exptheme_detail.html",
                context=self.context,
                cname=cname,
                favstate=isfav,
                apk=apk,
                tags=tags,
                referer=referer,
                skip=skip,
                front=front,
                end=end,
               )

class SearchHandler(BaseHandler):
    def get(self):
        skip = self.get_argument("skip",default=None)
        keyword = self.get_argument("keyword",default=None)
        if not skip or not keyword:
            raise tornado.web.HTTPError(500)
        skip = int(skip)
        if skip<0: skip=0
        words = keyword.strip()

        key = ' '.join(words.split())
        key = key.replace(' ','|')

        reg = ''
        try:
            reg = re.compile(ur'%s' % key, re.IGNORECASE)
        except:
            return self.notfound()

        taglist = theme_mongo.theme2tag.find({'name': reg},skip=skip,limit=2).sort('num',DESCENDING)

        front = skip-1
        if taglist.count()>skip:
            tag=taglist[0]
        end = skip+1
        if end>=taglist.count():
            end = -1
        if tag:
            apk = theme_mongo.apk.find_one({'_id':tag['apkid']})

        tags = []
        cname = None
        if apk:
            tags = theme_mongo.theme2tag.find({'apkid':apk['_id']})
            cate = theme_mongo.category.find_one({'_id':apk['cid']})
            if cate:
                cname = cate['name']
        referer = self.request.uri
        #referer = base64.encodestring(referer)
        referer = urllib.quote(referer)
        isfav = -1
        if self.session.uid:
            pri=theme_mongo.private.find_one({'uid':self.session.uid,'apkid':apk['_id']})
            if pri:
                isfav=1
            else:
                isfav=0

        self.render("seatheme_detail.html",
                context=self.context,
                cname=cname,
                favstate=isfav,
                apk=apk,
                keyword=keyword,
                tags=tags,
                referer=referer,
                skip=skip,
                front=front,
                end=end,
               )
