#!/usr/bin/env python
#-*- coding: utf-8 -*-

import re
import urllib
import json
import base64
import random
import datetime
import tornado
from db import mongo
from db import live_mongo
from db import theme_mongo
from pymongo import DESCENDING, ASCENDING
from bson import objectid
from libs import BaseHandler
from conf import config

newlist = ['4e4d610cdf714d2966000002','4fb479f75ba1c65561000027','4e4d610cdf714d2966000003','4fb47a305ba1c60ca5000223','4ef0a35c0569795756000000','4e4d610cdf714d2966000001'] #风景、视觉、动漫、城市、情感、动物
hotlist = ['4e4d610cdf714d2966000000','4e4d610cdf714d2966000002','4fb479f75ba1c65561000027','4fb47a465ba1c65561000028','4e4d610cdf714d2966000006','4e58c2570569791a19000000'] #美女、风景、视觉、物语、男人、影视


class CommendHandler(BaseHandler):
    def get(self):
        weekpaper = None #recommend paper at week
        weeklive = None  # recommend live at week
        adimage = None

        #newest paper
        nlist = []
        for i in newlist:
            cid = objectid.ObjectId(i)
            img = mongo.image.find({'cid':cid},limit=1).sort('atime', DESCENDING)
            if img.count()>0:
                nlist.append(img[0])

        #hot paper
        try:
            _imglist, length = self.hot_image_cache.find_list(config.Cache.hot_image_cache, 0, 5)
            if _imglist:
                imglist = [json.loads(i) for i in _imglist]
            else:
                imglist = mongo.image.find(limit=6,skip=0).sort('rank',DESCENDING)
        except:
            imglist = mongo.image.find(limit=6,skip=0).sort('rank',DESCENDING)

        self.render("commend.html",
                context=self.context,
                news=nlist,
                hots=imglist,
                )


class NewCommendHandler(BaseHandler):
    def get(self):
        self.render("newcommend.html",
                context=self.context,
                )

class MoreNewPaperHandler(BaseHandler):
    def get(self):
        limit = 18
        skip = self.get_argument("skip",default=0)
        try:
           skip = int(skip)
        except:
            skip = 0

        imglist = mongo.image.find(limit=limit,skip=skip).sort('atime',DESCENDING)
        images = []
        index = skip
        for i in imglist:
            if not self.session.hd:
                netimg = str(i['thumb_fobj'])
            elif self.session.net=='pc':
                netimg = str(i['fobjs']['640x480'])
            else: # self.session.net=='wifi':
                netimg = str(i['fobjs']['160x120'])

            images.append({
                    'id':str(i['_id']),
                    'image':netimg,
                    'skip':index
                })
            index += 1

        self._buffer = json.dumps({'code':0,'resp':images})
        callback = self.get_argument('jsoncallback', default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)
        self.write(self._buffer)

class MoreNewLiveHandler(BaseHandler):
    def get(self):
        limit = 9 
        skip = self.get_argument("skip",default=0)
        try:
            skip = int(skip)
        except:
            skip = 0

        apklist = live_mongo.apk.find(skip=skip,limit=limit).sort('atime',DESCENDING)
        lives = []
        index = skip
        for i in apklist:
            lives.append({
                    'id':str(i['_id']),
                    'thumbid':str(i['thumbid'][0]),
                    'skip':index
                })
            index += 1

        self._buffer = json.dumps({'code':0,'resp':lives})
        callback = self.get_argument('jsoncallback', default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)
        self.write(self._buffer)

class NewPaperDetailHandler(BaseHandler):
    def get(self):
        imgid = self.get_argument("imgid",default=None)
        _skip = self.get_argument("skip",default=0)
        ctype = self.get_argument("type",default="date")
        showmsg = self.session.show_msg
        self.session.show_msg = None

        try:
            skip=int(_skip)
            if skip < 0:
                skip = 0
                _skip = None
        except:
            skip=0

        img=None
        read_from_cache = False

        try:
            if _skip:
                if ctype=='date':
                    img = mongo.image.find(skip=skip,limit=1).sort('atime',DESCENDING)[0]
                else:
                    try:
                        img = self.hot_image_cache.find_one(config.Cache.hot_image_cache, skip)
                        if img:
                            read_from_cache = True
                            img = json.loads(img)
                        else:
                            img = mongo.image.find(skip=skip,limit=1).sort('rank',DESCENDING)[0]
                    except:
                        img = mongo.image.find(skip=skip,limit=1).sort('rank',DESCENDING)[0]

            else:
                iid = objectid.ObjectId(imgid)
                img = mongo.image.find_one({'_id':iid})
                if not img:
                    raise
        except:
            raise
            return self.notfound()

        front = skip - 1
        end = skip + 1

        if not read_from_cache:
            if end>=mongo.image.count():
                end = -1
        else:
            if not self.hot_image_cache.find_one(config.Cache.hot_image_cache, end):
                end = -1

        if _skip == None:
            front = -1
            end = -1

        referer = urllib.quote(self.request.uri)
        isfav=-1
        if self.session.uid:
            pri=mongo.private.find_one({'uid':self.session.uid,'imgid': img['_id']})
            if pri:
                isfav=1
            else:
                isfav=0

        tags = mongo.img2tag.find({'imgid': objectid.ObjectId(img['_id'])}).sort('num', DESCENDING)
        tags =  [i for i in tags]
        self.render("compaper_detail.html",
                context=self.context,
                image=img,
                front=front,
                end=end,
                isfav=isfav,
                referer=referer,
                tags=tags,
                message=showmsg,
                type=ctype,
                )

class NewLiveDetailHandler(BaseHandler):
    def get(self):
        apkid = self.get_argument("apkid",default=None)
        skip = self.get_argument("skip",default=0)
        ctype = self.get_argument("type", default="date")

        try:
            skip=int(skip)
        except:
            skip=0

        apk=None
        try:
            if apkid==None:
                if ctype=='date':
                    apks=live_mongo.apk.find(skip=skip,limit=1).sort('atime',DESCENDING)
                else:
                    apks=live_mongo.apk.find(skip=skip,limit=1).sort('rank',DESCENDING)

                try:
                    apk=apks[0]
                    pid=apk['_id']
                except:
                    raise
            else:
                pid = objectid.ObjectId(apkid)
                apk = live_mongo.apk.find_one({'_id':pid})
            if not apk:
                raise
        except:
            return self.notfound()

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


        front = skip-1
        end = skip+1
        if end>=live_mongo.apk.count():
            end = -1

        referer = urllib.quote(self.request.uri)
        isfav=-1
        if self.session.uid:
            pri=live_mongo.private.find_one({'uid':self.session.uid,'apkid':pid})
            if pri:
                isfav=1
            else:
                isfav=0

        self.render("comlive_detail.html",
                context=self.context,
                apk=apk,
                front=front,
                end=end,
                favstate=isfav,
                referer=referer,
                score=score,
                amount=mcount,
                type=ctype,
                )

class HotCommendHandler(BaseHandler):
    def get(self):
        self.render("hotcommend.html",
                context=self.context,
                )

class MoreHotPaperHandler(BaseHandler):
    def get(self):
        limit = 18
        skip = self.get_argument("skip",default=0)
        try:
           skip = int(skip)
        except:
            skip = 0

        try:
            _imglist, length = self.hot_image_cache.find_list(config.Cache.hot_image_cache, skip, limit-1)
            if _imglist:
                imglist = [json.loads(i) for i in _imglist]
            else:
                imglist = mongo.image.find(limit=limit,skip=skip).sort('rank',DESCENDING)
        except:
            imglist = mongo.image.find(limit=limit,skip=skip).sort('rank',DESCENDING)


        images = []
        index = skip
        for i in imglist:
            if not self.session.hd:
                netimg = str(i['thumb_fobj'])
            elif self.session.net=='pc':
                netimg = str(i['fobjs']['640x480'])
            else: # self.session.net=='wifi':
                netimg = str(i['fobjs']['160x120'])

            images.append({
                    'id':str(i['_id']),
                    'image':netimg,
                    'skip':index
                })
            index += 1

        self._buffer = json.dumps({'code':0,'resp':images})
        callback = self.get_argument('jsoncallback', default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)
        self.write(self._buffer)

class MoreHotLiveHandler(BaseHandler):
    def get(self):
        limit = 9
        skip = self.get_argument("skip",default=0)
        try:
            skip = int(skip)
        except:
            skip = 0

        apklist = live_mongo.apk.find(skip=skip,limit=limit).sort('rank',DESCENDING)
        lives = []
        index = skip
        for i in apklist:
            lives.append({
                    'id':str(i['_id']),
                    'thumbid':str(i['thumbid'][0]),
                    'skip':index
                })
            index += 1

        self._buffer = json.dumps({'code':0,'resp':lives})
        callback = self.get_argument('jsoncallback', default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)
        self.write(self._buffer)

