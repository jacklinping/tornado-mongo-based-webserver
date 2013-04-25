# -*- coding: utf-8 -*-

import tornado
import datetime
import base64
import json
from pymongo import DESCENDING, ASCENDING
from bson import objectid
from libs import BaseHandler
from db import mongo,live_mongo,theme_mongo
from conf import config
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class ThumbHandler(BaseHandler):
    def get(self,thumbid):
        ctype = self.get_argument("type",default=1)
        ctype = int(ctype)
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

class ApkDataHandler(BaseHandler):
    def get(self,apkid):
        try:
            pid = objectid.ObjectId(apkid)
            apk = live_mongo.find_one({'_id':pid})
            if not apk:
                raise
        except:
            raise tornado.web.HTTPError(404)

        return apk

class LiveFavoriteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,liveid=None):
        ctype = self.get_argument('type',default=None)
        if not ctype:
            raise tornado.web.HTTPError(404)
        ctype = int(ctype)
        referer = self.get_argument('referer',default=None)
        if not referer:
            referer = '/index'
        try:
            lid = objectid.ObjectId(liveid)
            if ctype==1:
                apk = live_mongo.apk.find_one({'_id':lid})
            else:
                apk = theme_mongo.apk.find_one({'_id':lid})
            if not apk:
                raise
        except:
            raise tornado.web.HTTPError(404)

    #    referer = base64.decodestring(referer)
        if ctype==1:
            if live_mongo.private.find_one({'apkid':lid,'uid':self.session.uid}):
                return
            live_mongo.apk.update({'_id':lid},
                    {'$set':{
                        'rank':int(apk['rank'])+1
                        }
                        })
            live_mongo.private.insert({
                'uid':self.session.uid,
                'apkid':lid,
                'atime':datetime.datetime.now()
                })
        else:
            if theme_mongo.private.find_one({'apkid':lid,'uid':self.session.uid}):
                return
            theme_mongo.apk.update({'_id':lid},
                    {'$set':{
                        'rank':int(apk['rank'])+1
                        }
                        })
            theme_mongo.private.insert({
                'uid':self.session.uid,
                'apkid':lid,
                'atime':datetime.datetime.now()
                })
       # return self.redirect(referer)


class LiveDisFavoriteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,liveid=None):
        ctype = self.get_argument('type',default=None)
        if not ctype:
            raise tornado.web.HTTPError(404)
        ctype = int(ctype)
        referer = self.get_argument('referer',default=None)
     #   referer = base64.decodestring(referer)
        if not referer:
            referer = '/index'
        try:
            lid = objectid.ObjectId(liveid)
            if ctype==1:
                apk = live_mongo.apk.find_one({'_id':lid})
            else:
                apk = theme_mongo.apk.find_one({'_id':lid})
            if not apk:
                raise
        except:
            raise tornado.web.HTTPError(404)
        if ctype==1:
            live_mongo.apk.update({'_id':lid},
                    {'$set':{
                        'rank':int(apk['rank'])-1
                        }
                        })
            live_mongo.private.remove({
                'uid':self.session.uid,
                'apkid':lid,
                })
        else:
            theme_mongo.apk.update({'_id':lid},
                    {'$set':{
                        'rank':int(apk['rank'])-1
                        }
                        })
            theme_mongo.private.remove({
                'uid':self.session.uid,
                'apkid':lid,
                })
        #return self.redirect(referer)


#for download apk rank +1
class AddRankHandler(BaseHandler):
    def get(self,liveid=None):
        ctype = self.get_argument('type',default=None)
        if not ctype:
            raise tornado.web.HTTPError(404)
        ctype = int(ctype)
        apk = None
        try:
            lid = objectid.ObjectId(liveid)
            if ctype==1:
                apk = live_mongo.apk.find_one({'_id':lid})
            else:
                apk = theme_mongo.apk.find_one({'_id':lid})
        except:
            pass

        if apk:
            if ctype==1:
                live_mongo.apk.update({'_id':lid},
                        {'$set':{
                            'rank':int(apk['rank'])+1
                            }
                            })
            else:
                theme_mongo.apk.update({'_id':lid},
                        {'$set':{
                            'rank':int(apk['rank'])+1
                            }
                            })
            _buffer = json.dumps({'code':0})
        else:
            _buffer = json.dumps({'code':-1})

        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            _buffer = "%s(%s)" % (callback,_buffer)
        self.write(_buffer)


class CheckHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass

    def get(self):
        pass

    def post(self):
        packages = self.get_argument('packages',default=None)
        if not packages:
            return self.write('{}')

        namelist = packages.split(',')
        if not namelist or len(namelist)<1:
            self.write('[]')

        checklist = []
        for item in namelist:
            apk = live_mongo.apk.find_one({'package_name':item})
            if apk:
                link = config.Server.apk_server+'/'+str(apk['savepath'])
                pdict = {'name':item,'version':str(apk['package_version']),'link':link,'filename':str(apk['name']),'size':str(apk['package_size'])}
                checklist.append(pdict)

        _buffer = json.dumps({'live':checklist})
        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            _buffer = "%s(%s)" % (callback,_buffer)
        self.write(_buffer)

class PaperFavoriteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        _imgid = self.get_argument('imgid',default=None)
        referer = self.get_argument('referer',default=None)

        #referer = base64.decodestring(referer)
        imgid = None
        try:
            imgid = objectid.ObjectId(_imgid)
            if not mongo.image.find_one({'_id': imgid}):
                raise
        except:
            raise

        mongo.image.update(
                {'_id': imgid},
                {'$inc': {'favs': 1}}
                )

        if not mongo.private.find_one(
                {'uid': self.session.uid, 'imgid': imgid}):
            mongo.private.insert({
                'uid': self.session.uid,
                'imgid': imgid,
                'atime': datetime.datetime.now()
                })


class PaperDisFavoriteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        _imgid = self.get_argument('imgid',default=None)
        referer = self.get_argument('referer',default=None)

        #referer = base64.decodestring(referer)
        imgid = None
        try:
            imgid = objectid.ObjectId(_imgid)
            if not mongo.image.find_one({'_id': imgid}):
                raise
        except:
            raise

        mongo.image.update(
                {'_id': imgid},
                {'$inc': {'favs': -1}}
                )

        mongo.private.remove({'uid': self.session.uid, 'imgid': imgid})
        #return "{'ret': 1}"
        #self.redirect(referer, permanent=False)

class PaperFollowDirHandler(BaseHandler):
    def get(self):
        _dirid = self.get_argument("dirid",default=None)

        if not _dirid:
            raise

        dirid = None
        dir = None
        try:
            dirid = objectid.ObjectId(_dirid)
            dir = mongo.dir.find_one({'_id': dirid})
            if not dir: raise
        except:
            raise

        fd = mongo.followdir.find_one({'dirid': dirid, 'uid': self.session.uid})
        if not fd:
            mongo.followdir.insert({
                'dirid': dirid,
                'uid': self.session.uid,
                'atime': datetime.datetime.now()
                })

            dir['follownum'] += 1
            mongo.dir.save(dir)


class PaperUnfollowDirHandler(BaseHandler):
    def get(self):
        _dirid = self.get_argument("dirid",default=None)

        if not _dirid:
            raise

        dirid = None
        dir = None
        try:
            dirid = objectid.ObjectId(_dirid)
            dir = mongo.dir.find_one({'_id': dirid})
            if not dir: raise
        except:
            raise

        try:
            mongo.followdir.remove({'dirid': dirid, 'uid': self.session.uid})
        except:
            pass
        else:
            if dir['follownum'] > 0:
                dir['follownum'] -= 1
                mongo.dir.save(dir)

class LiveMarkHandler(BaseHandler):
    def get(self):
        score = self.get_argument("score",default=0)
        apkid = self.get_argument("apkid",default=None)
        try:
            score = int(score)
            if score<0 or score>5:
                raise
        except:
            score = 3
        try:
            user = mongo.user.find_one({'_id':self.session.uid})
            if not user:
                raise
        except:
            return

        try:
            pid = objectid.ObjectId(apkid)
            apk = live_mongo.apk.find_one({'_id':pid})
            if not apk:
                raise
        except:
            return

        mark = live_mongo.mark2apk.find_one({'apkid':pid,'uid':self.session.uid})
        if mark:
            live_mongo.mark2apk.update({'apkid':pid,'uid':self.session.uid},{'$set':{'mark':score}})
        else:
            live_mongo.mark2apk.insert({
                'apkid':pid,
                'uid':self.session.uid,
                'mark':score
                })
