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


class ExplorerHandler(BaseHandler):

    def get(self):
        self.render("explorer.html",
                context=self.context,
                )

class MoreExplorerHandler(BaseHandler):
    def _random_wallpaper(self):
        wallpapers = []
        limit=18
        for i in mongo.setting_log.find(limit=limit*4).sort('atime', DESCENDING):

            img = mongo.image.find_one({'_id': i['imgid']})
            if not img:
                continue
            if str(img['_id']) not in [j['_id'] for j in wallpapers]:
                if not self.session.hd:
                    item = {'src':"http://"+self.context['static_server']+"/download/"+img['thumb_fobj'],
                'href':"/exppaperDetail/"+str(img['_id'])+"#t1:0"+"#t0:0",
                '_id':str(img['_id'])}
                elif self.session.net == 'pc':
                    item = {'src':"http://"+self.context['static_server']+"/download/"+img['fobjs']['640x480'],
                'href':"/exppaperDetail/"+str(img['_id'])+"#t1:0"+"#t0:0",
                '_id':str(img['_id'])}
                else: #if self.session.net == 'wifi':
                    item = {'src':"http://"+self.context['static_server']+"/download/"+img['fobjs']['160x120'],
                'href':"/exppaperDetail/"+str(img['_id'])+"#t1:0"+"#t0:0",
                '_id':str(img['_id'])}
                
                wallpapers.append(item)

            if len(wallpapers) >= limit:
                break
        return wallpapers

    def _random_live(self):
        cates = list(live_mongo.category.find())
        selcates = []
        while len(selcates)<7:
            selcates.extend(cates)

        src = []
        imgtype = []
        href = []
        lives = []
        j =0
        offset = random.randrange(0,5)
        for i in selcates:
            if j<6:
                apks = live_mongo.apk.find({'cid':i['_id']},skip=offset,limit=1)
                try:
                    apk=apks[0]
                    item={'src':"http://"+self.context['static_server']+"/thumbnail/"+str(apk['thumbid'][0])+"?type=1",
                    'href':"/expliveDetail/"+str(apk['_id'])+"#t1:0"+"#t0:0"}
                    lives.append(item)
                    j=j+1
                except:
                    continue
            else:
                break
        return lives

    def _random_theme(self):
        cates = list(theme_mongo.category.find())
        selcates = []
        if len(cates)>2:
            selcates = random.sample(cates,2)
        elif len(cates)>0:
            selcates.extend(cates)
        src = []
        imgtype = []
        href = []
        themes = []
        for i in selcates:
            apks = theme_mongo.apk.find({'cid':i['_id']})
            if apks.count()<=0:
                return None
            skip = random.randrange(0,apks.count())
            apk = apks.skip(skip).limit(1)[0]
            if apk:
                item = {'src':"http://"+self.context['static_server']+"/thumbnail/"+str(apk['thumbid'][0])+"?type=2",
				'href':"/expthemeDetail?cateid="+str(apk['cid'])+"&skip="+str(skip)+"#t1:0"+"#t0:0"}
                themes.append(item)

        return themes

    def get(self):
        wallpapers = self._random_wallpaper()
        lives = self._random_live()
       # themes = self._random_theme()

        #self._buffer = json.dumps({'code':0,'paper':wallpapers,'live':lives,'theme':themes})
        self._buffer = json.dumps({'code':0,'paper':wallpapers,'live':lives})
        callback = self.get_argument('jsoncallback', default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)
        self.write(self._buffer)

class PaperDetailHandler(BaseHandler):
    def get(self,imgid):
        iid = objectid.ObjectId(imgid)
        img = mongo.image.find_one({'_id':iid})
        tags = []
        if img:
            tags = mongo.img2tag.find({'imgid':img['_id']}).sort('num', DESCENDING)
            mongo.image.update({'_id': img['_id']}, {'$inc': {'views': 1}})
        referer = self.request.uri
        referer = urllib.quote(referer)
        isfav =-1
        if self.session.uid:
            pri=mongo.private.find_one({'uid':self.session.uid,'imgid':img['_id']})
            if pri:
                isfav=1
            else:
                isfav=0
        showmsg = self.session.show_msg
        self.session.show_msg = None
        self.render("exppaper_detail.html",
                context=self.context,
                referer=referer,
                message = showmsg,
                favstate=isfav,
                image=img,
                tags=tags,
               # skip=skip,
               # front=front,
                width=self.session.width,
                height=self.session.height,
                login=self.session.login,
                id=self.session.uid,
                #end=end,
                net=self.session.net,
               )

class LiveDetailHandler(BaseHandler):
    def get(self,apkid):
        apk = None
        try:
            aid = objectid.ObjectId(apkid)
            apk = live_mongo.apk.find_one({'_id':aid})
        except:
            return tornado.web.HTTPError(404)
        tags = []
        if apk:
            tags = live_mongo.apk2tag.find({'apkid':apk['_id']})

        #cal mark
        marks = live_mongo.mark2apk.find({'apkid':apk['_id']})
        msum = 0.0
        mcount = 0
        for m in marks:
            print str(m)
            msum += m['mark']
            mcount += 1
        score = 0
        if mcount>0:
            score = round(msum/mcount)
            score = int(score)

        try:
            cid = apk['cid'] 
            cate = live_mongo.category.find_one({'_id':cid})
            if not cate:
                raise
        except:
            raise tornado.web.HTTPError(500)
        cname = cate['name']
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
        self.render("explive_detail.html",
                context=self.context,
                cname=cname,
                favstate=isfav,
                apk=apk,
                tags=tags,
                referer=referer,
                score=score,
                amount=mcount,
               # skip=skip,
               # front=front,
               # end=end,
               )
