#-*- coding: utf-8 -*-

import tornado
import json
import base64
import re
from pymongo import DESCENDING, ASCENDING
from bson import objectid
from libs import BaseHandler
from db import live_mongo
import urllib

class CategoryHandler(BaseHandler):
    def get(self):
        cates = live_mongo.category.find()
        if not cates:
            raise tornado.web.HTTPError(404)

        lives = []
        for i in cates:
            lives.append({
                'id':str(i['_id']),
                'thumbid':str(i['thumbid']),
                'name':i['name']
                })


        _buffer = json.dumps({'code':0, 'resp':lives})
        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            _buffer = "%s(%s)" % (callback,_buffer)
        self.write(_buffer)


class ListHandler(BaseHandler):
    limit =18

    def get(self):
        cateid = self.get_argument("cateid", default=None)
        skip = self.get_argument("skip", default=0)
        order = self.get_argument("order",default=None)
        if not skip:
            skip = 0
        if not order:
            order = 'newest'
        try:
            cid = objectid.ObjectId(cateid)
        except:
            raise tornado.web.HTTPError(404)

        cate = live_mongo.category.find_one({'_id':cid})
        if cate:
            cname = cate['name']
        if not skip: skip = 0

        self.render("live_list.html",
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


class DetailHandler(BaseHandler):
    def get(self,apkid):
        try:
            pid = objectid.ObjectId(apkid)
            apk = live_mongo.apk.find_one({'_id':pid})
            if not apk:
                raise
        except:
            raise tornado.web.HTTPError(404)

        #cal mark
        marks = live_mongo.mark2apk.find({'apkid':pid})
        msum = 0.0
        mcount = 0
        for m in marks:
            msum += m['mark']
            mcount += 1
        score = 0
        if mcount>0:
            score = round(msum/mcount)
            score = int(score)


        skip = self.get_argument("skip",default=None)
        if not skip: skip=0
        order = self.get_argument("order",default=None)
        if not order: order='newest'
        skip = int(skip)

        cate = live_mongo.category.find_one({'_id':apk['cid']})
        cname = ''
        if cate:
            cname = cate['name']
        tags = live_mongo.apk2tag.find({'apkid':pid})
        if order == 'newest':
            listcount = live_mongo.apk.find({'cid':apk['cid']},skip=skip,limit=3).sort('atime',DESCENDING).count()
        else:
            listcount = live_mongo.apk.find({'cid':apk['cid']},skip=skip,limit=3).sort('rank',DESCENDING).count()

        front = skip-1
        end = skip+1
        if end>=listcount:
            end = -1

        referer = self.request.uri
       # referer = base64.encodestring(referer)
        referer = urllib.quote(referer)
        isfav = -1
        if self.session.uid:
            pri=live_mongo.private.find_one({'uid':self.session.uid,'apkid':apk['_id']})
            if pri:
                isfav=1
            else:
                isfav=0

        self.render("live_detail.html",
                context=self.context,
                cname=cname,
                favstate=isfav,
                apk=apk,
                tags=tags,
                referer=referer,
                order=order,
                skip=skip,
                front=front,
                end=end,
                score=score,
                amount=mcount,
                )

class MoreListHandler(BaseHandler):
    def get(self):
        limit = 18
        cateid = self.get_argument("cateid", default=None)
        skip = self.get_argument("skip", default=0)
        order = self.get_argument("order",default=None)
        if not skip:
            skip = 0
        skip = int(skip)
        if skip<1:
            limit = 9
        if not order:
            order = 'newest'
        try:
            cid = objectid.ObjectId(cateid)
        except:
            raise tornado.web.HTTPError(404)

        lives = []
        if order == 'newest':
            livelist = live_mongo.apk.find({'cid':cid}, skip=skip, limit=limit).sort('atime',DESCENDING)
        else:
            livelist = live_mongo.apk.find({'cid':cid}, skip=skip, limit=limit).sort('rank',DESCENDING)

        for i in livelist:
            lives.append({
                    '_id': str(i['_id']),
                    'name': i['name'],
            #        'pname': i['package_name'],
            #        'pversoin':i['package_version'],
            #        'psize':i['package_size'],
            #        'picon':i['package_icon'],
                    'cid': str(i['cid']),
            #        'uid': str(i['uid']),
                    'thumbid': str(i['thumbid'][0]),
            #        'savepath': i['savepath'],
            #        'descr': i['descr'],
            #        'atime': i['atime'],
                })
        self._buffer = json.dumps({'code':0, 'resp':lives})
        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)

        self.write(self._buffer)

class LiveOrderHandler(BaseHandler):
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
            cate = live_mongo.category.find_one({'_id':cid})
            if not cate:
                raise
        except:
            raise tornado.web.HTTPError(500)
        cname = cate['name']

        if order == 'newest':
            apks = live_mongo.apk.find({'cid':cid}, skip=skip, limit=2).sort('atime',DESCENDING)
        else:
            apks = live_mongo.apk.find({'cid':cid}, skip=skip, limit=2).sort('rank',DESCENDING)
        front = skip-1
        if apks.count()>skip:
            apk=apks[0]
        end = skip+1
        if end>=apks.count():
            end = -1
#        tags = []
#        if apk:
#            tags = live_mongo.apk2tag.find({'apkid':apk['_id']})

        #cal mark
        marks = live_mongo.mark2apk.find({'apkid':apk['_id']})
        msum = 0.0
        mcount = 0
        for m in marks:
            msum += m['mark']
            mcount += 1
        score = 0
        if mcount>0:
            score = round(msum/mcount)
            score = int(score)

        referer = self.request.uri
        #referer = base64.encodestring(referer)
        referer = urllib.quote(referer)
        isfav = -1
        if self.session.uid:
            pri=live_mongo.private.find_one({'uid':self.session.uid,'apkid':apk['_id']})
            if pri:
                isfav=1
            else:
                isfav=0
        self.render("live_detail.html",
                context=self.context,
                cname=cname,
                favstate=isfav,
                apk=apk,
                #tags=tags,
                referer=referer,
                skip=skip,
                order=order,
                front=front,
                end=end,
                score=score,
                amount=mcount,
               )





class TipsHandler(BaseHandler):
    def get(self):
        self.render("liveTips.html",
                context=self.context,
                )

