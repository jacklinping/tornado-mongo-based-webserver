#-*- coding: utf-8 -*-

import tornado
import uuid
import urllib
import os,sys
import datetime
import Image
import StringIO
from bson import objectid
from pymongo import DESCENDING, ASCENDING

from apk import save_apk, analyze_apk
from conf import config
from libs import BaseHandler
from db import live_mongo,theme_mongo

def make_thumb(img_buffer,img_name,newwidth):
    origin_img = Image.open(StringIO.StringIO(img_buffer))

    x,y = origin_img.size

    rwidth = newwidth
    rheight = (rwidth*y)/x
    zoom_img = origin_img.resize((rwidth,rheight), Image.ANTIALIAS)

    tmp_img = "/tmp/%s-%s" % (str(uuid.uuid4()), img_name)
    zoom_img.save(tmp_img, format="JPEG")

    return tmp_img 

def save_thumb(fileValue,ctype):
    if not fileValue:
        return None
    if ctype==1:
        zoomimg = make_thumb(fileValue['body'],'zoomimg',160)
        thumbid = live_mongo.filefs.put(open(zoomimg).read())
        originimg = make_thumb(fileValue['body'],'originimg',320)
        originid = live_mongo.filefs.put(open(originimg).read())
    else:
        zoomimg = make_thumb(fileValue['body'],'tzoomimg',160)
        thumbid = theme_mongo.filefs.put(open(zoomimg).read())
        originimg = make_thumb(fileValue['body'],'toriginimg',320)
        originid = theme_mongo.filefs.put(open(originimg).read())
    return thumbid,originid



class UploadHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,cateid):
        ctype = self.get_argument("type",default=1)
        ctype = int(ctype)

        try:
            cid = objectid.ObjectId(cateid)
        except:
            raise tornado.web.HTTPError(404)

        category = None
        if ctype==1:
            category = live_mongo.category.find_one({
                '_id':cid
                })
        else:
            category = theme_mongo.category.find_one({
                '_id':cid
                })

        if not category:
            raise tornado.web.HTTPError(404)

        self.render("upload.html",
                category=category,
                type = ctype,
                )

    @tornado.web.authenticated
    def post(self,catId):
        print 'upload post handler'
        ctype = self.get_argument("type", default=1)
        ctype = int(ctype)
        apkname = self.get_argument("name", default='')
        author = self.get_argument("author", default='')
        origin = self.get_argument("from", default='')
        descr = self.get_argument("desc", default='')
        tag = self.get_argument("tag",default='')
        cateid = self.get_argument("cateid", default=None)

        thumbViews,apkData = None,None
        if self.request.files:
            thumbViews = self.request.files['thumb']
            apkData = self.request.files['apk'][0]

        name = apkname.strip()
        descr = descr.strip()
        try:
            cid = objectid.ObjectId(cateid)
            if ctype==1:
                cate = live_mongo.category.find_one({'_id': cid})
            else:
                cate = theme_mongo.category.find_one({'_id': cid})

            if not cate:
                raise
        except:
            raise tornado.web.HTTPError(404)

        if not name or not descr:
            self.message='输入不正确'
            return self.render("upload.html",
                    category=cate,
                    type=ctype,
                    )

        try:
            apkpath,apksize,relatypath = save_apk(apkData)
            package_name, package_version, iconId = analyze_apk(apkpath)
        except:
            raise
            self.message = '保存，解析包错误'
            return self.render("upload.html",
                    category=cate,
                    type=ctype,
                    )

        if not package_name:
            self.message = message='包名解析错误'
            return self.render("upload.html",
                    category=cate,
                    type=ctype,
                    )
        if not package_version:
            self.message='版本号解析错误'
            return self.render("upload.html",
                    category=cate,
                    type=ctype,
                    )
        if not iconId:
            self.message='图标解析错误'
            return self.render("upload.html",
                    category=cate,
                    type=ctype,
                    )

        thumbid,originids = [],[]
        for i in xrange(0,len(thumbViews)):
            tid,oid = save_thumb(thumbViews[i],ctype)
            thumbid.append(tid)
            originids.append(oid)

        if ctype==1:
            apkid = live_mongo.apk.insert({
                'name': name,
                'package_name': package_name,
                'package_version': package_version,
                'package_size': apksize,
                'package_icon': iconId,
                'uid': self.session.uid,
                'cid': cid,
                'savepath': relatypath,
                'descr': descr,
                'thumbid': thumbid,
                'originids': originids,
                'author': author,
                'origin': origin,
                'rank': 1,
                'atime': datetime.datetime.now(),
                })
        else:
            apkid = theme_mongo.apk.insert({
                'name': name,
                'package_name': package_name,
                'package_version': package_version,
                'package_size': apksize,
                'package_icon': iconId,
                'uid': self.session.uid,
                'cid': cid,
                'savepath': relatypath,
                'descr': descr,
                'author': author,
                'origin': origin,
                'thumbid': thumbid,
                'originids':originids,
                'rank':1,
                'atime': datetime.datetime.now(),
                })
        if len(tag)>0:
            if tag[-1:]==',':
                tag = tag[:-1]
        tags = tag.split(',')

        for item in tags:
            stag = None
            if ctype==1:
                stag = live_mongo.tag.find_one({"name":item})
                if not stag:
                    live_mongo.tag.insert({
                        'name':item,
                        'uid':self.session.uid,
                        'rank':1,
                        'atime':datetime.datetime.now(),
                        })
                live_mongo.apk2tag.insert({
                        'name':item,
                        'uids':[self.session.uid],
                        'apkid':apkid,
                        'num':1,
                        'atime':datetime.datetime.now(),
                    })
            else:
                stag = theme_mongo.tag.find_one({"name":item})
                if not stag:
                    theme_mongo.tag.insert({
                        'name':item,
                        'uid':self.session.uid,
                        'rank':1,
                        'atime':datetime.datetime.now(),
                        })
                theme_mongo.theme2tag.insert({
                        'name':item,
                        'uids':[self.session.uid],
                        'apkid':apkid,
                        'num':1,
                        'atime':datetime.datetime.now(),
                    })

            return self.redirect('/live/home/d')

class ModifyHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,apkid):
        print 'modify handler'
        ctype = self.get_argument("type",default=1)
        ctype = int(ctype)
        try:
            pid = objectid.ObjectId(apkid)
            if ctype==1:
                apk = live_mongo.apk.find_one({'_id':pid})
            else:
                apk = theme_mongo.apk.find_one({'_id':pid})
            if not apk:
                raise
        except:
            raise tornado.web.HTTPError(404)
        if ctype==1:
            cates = live_mongo.category.find()
            tags = live_mongo.apk2tag.find({'apkid':pid})
            taglist = []
            for i in tags:
                taglist.append(i['name'])
            if taglist:
                tag = ','.join(taglist)
            else:
                tag = ''
        else:
            cates = theme_mongo.category.find()
            tags = theme_mongo.theme2tag.find({'apkid':pid})
            taglist = []
            for i in tags:
                taglist.append(i['name'])
            if taglist:
                tag = ','.join(taglist)
            else:
                tag =''

        if not cates:
            return self.redirect("/home")

        self.render("modify.html",
                apk=apk,
                tag=tag,
                categorys=cates,
                type=ctype,
                )

    @tornado.web.authenticated
    def post(self,apkid):
        print 'modify post handler'
        ctype = self.get_argument("type", default=1)
        ctype = int(ctype)
        apkname = self.get_argument("name", default='')
        author = self.get_argument("author", default='')
        origin = self.get_argument("from", default='')
        tag = self.get_argument("tag", default='')
        descr = self.get_argument("desc", default='')
        cateid = self.get_argument("cateid", default=None)
        thumbViews,apkData = [],None
        if self.request.files:
            for upName,upFiles in self.request.files.items():
           # print str(self.request.files['apk'])
                if upName == 'thumb':
                    thumbViews = self.request.files['thumb']
                elif upName == 'apk':
                    apkData = self.request.files['apk'][0]

        name = apkname.strip()
        descr = descr.strip()
        try:
            cid = objectid.ObjectId(cateid)
            if ctype==1:
                cate = live_mongo.category.find_one({'_id': cid})
            else:
                cate = theme_mongo.category.find_one({'_id': cid})
            if not cate:
                raise
        except:
            raise tornado.web.HTTPError(404)

        try:
            pid = objectid.ObjectId(apkid)
            if ctype==1:
                apk = live_mongo.apk.find_one({'_id':pid})
            else:
                apk = theme_mongo.apk.find_one({'_id':pid})

            if not apk:
                raise
        except:
            raise tornado.web.HTTPError(404)
        if ctype==1:
            cates = live_mongo.category.find()
        else:
            cates = theme_mongo.category.find()

        if not cates:
            return self.redirect("/home")

        if not name or not descr:
            self.message='输入不正确'
            return self.render("modify.html",
                    apk=apk,
                    tag=tag,
                    categorys=cates,
                    type = ctype,
                    )
        if ctype==1:
            tempApk = live_mongo.apk.find_one({'name':name})
        else:
            tempApk = theme_mongo.apk.find_one({'name':name})

        if tempApk and str(tempApk['_id'])!=str(apkid):
            self.message='文件名有重复'
            return self.render("modify.html",
                    apk=apk,
                    tag=tag,
                    categorys=cates,
                    type=ctype,
                    )
        apkpath,thumbid=None,None
        if apkData:
            try:
                apkpath,apksize,relatypath = save_apk(apkData)
                if apkpath:
                    try:
                        package_name,package_version,iconId=analyze_apk(apkpath)
                    except:
                        self.message='解析包错误'
                        return self.render("modify.html",
                                apk=apk,
                                tag=tag,
                                categorys=cates,
                                type=ctype,
                                )
                    errMsg = None
                    if not package_name:
                        errMsg = '包名解析错误'
                    elif not package_version:
                        errMsg = '版本号解析错误'
                    elif not iconId:
                        errMsg = '图标解析错误'
                    if errMsg != None:
                        return self.render("modify.html",
                                message=errMsg,
                                apk=apk,
                                tag=tag,
                                categorys=cates,
                                type=ctype,
                                )
            except:
                self.message='保存包错误'
                return self.render("modify.html",
                        apk=apk,
                        tag=tag,
                        categorys=cates,
                        type=ctype,
                        )

        thumbid, originids = [],[]
        for i in xrange(0,len(thumbViews)):
            tid,oid = save_thumb(thumbViews[i],ctype)
            thumbid.append(tid)
            originids.append(oid)

        if len(tag)>0:
            if tag[-1:]==',':
                tag = tag[:-1]
        tags = tag.split(',')
        if ctype==1:
            live_mongo.apk2tag.remove({'apkid':apk['_id']})
        else:
            theme_mongo.theme2tag.remove({'apkid':apk['_id']})

        for item in tags:
            stag = None
            if ctype==1:
                stag = live_mongo.tag.find_one({"name":item})
                if not stag:
                    live_mongo.tag.insert({
                        'name':item,
                        'uid':self.session.uid,
                        'rank':1,
                        'atime':datetime.datetime.now(),
                        })
                live_mongo.apk2tag.insert({
                        'name':item,
                        'uids':[self.session.uid],
                        'apkid':pid,
                        'num':1,
                        'atime':datetime.datetime.now(),
                    })
            else:
                stag = theme_mongo.tag.find_one({"name":item})
                if not stag:
                    theme_mongo.tag.insert({
                        'name':item,
                        'uid':self.session.uid,
                        'rank':1,
                        'atime':datetime.datetime.now(),
                        })
                theme_mongo.theme2tag.insert({
                        'name':item,
                        'uids':[self.session.uid],
                        'apkid':pid,
                        'num':1,
                        'atime':datetime.datetime.now(),
                    })

        if apkpath and thumbid:
            if ctype==1:
                live_mongo.apk.update(
                        {'_id':apk['_id']},
                        {'$set':{
                            'name':name,
                            'package_name':package_name,
                            'package_version':package_version,
                            'package_size':apksize,
                            'package_icon':iconId,
                            'uid':self.session.uid,
                            'cid':cid,
                            'savepath':relatypath,
                            'author': author,
                            'origin': origin,
                            'descr':descr,
                            'thumbid':thumbid,
                            'originids':originids,
                            }
                            }
                        )
                return self.redirect('/live/home/%s/0' % str(cid))
            else:
                theme_mongo.apk.update(
                        {'_id':apk['_id']},
                        {'$set':{
                            'name':name,
                            'package_name':package_name,
                            'package_version':package_version,
                            'package_size':apksize,
                            'package_icon':iconId,
                            'uid':self.session.uid,
                            'cid':cid,
                            'savepath':relatypath,
                            'descr':descr,
                            'author':author,
                            'origin': origin,
                            'thumbid':thumbid,
                            'originids':originids,
                            }
                            }
                        )
                return self.redirect('/theme/home/d')
        elif apkpath:
            if ctype==1:
                live_mongo.apk.update(
                        {'_id':apk['_id']},
                        {'$set':{
                            'name':name,
                            'package_name':package_name,
                            'package_version':package_version,
                            'package_size':apksize,
                            'package_icon':iconId,
                            'uid':self.session.uid,
                            'cid':cid,
                            'savepath':relatypath,
                            'descr':descr,
                            'author':author,
                            'origin':origin,
                            }
                            }
                        ) 
                return self.redirect('/live/home/%s/0' % str(cid))
            else:
                theme_mongo.apk.update(
                        {'_id':apk['_id']},
                        {'$set':{
                            'name':name,
                            'package_name':package_name,
                            'package_version':package_version,
                            'package_size':apksize,
                            'package_icon':iconId,
                            'uid':self.session.uid,
                            'cid':cid,
                            'savepath':relatypath,
                            'descr':descr,
                            'author':author,
                            'origin':origin,
                            }
                            }
                        )

                return self.redirect('/theme/home/d')
        elif thumbid:
            if ctype==1:
                live_mongo.apk.update(
                        {'_id':apk['_id']},
                        {'$set':{
                            'name':name,
                            'uid':self.session.uid,
                            'cid':cid,
                            'descr':descr,
                            'author':author,
                            'origin':origin,
                            'rank':1,
                            'thumbid':thumbid,
                            'originids':originids,
                            }
                            }
                        )
                return self.redirect('/live/home/%s/0' % str(cid))
            else:
                theme_mongo.apk.update(
                        {'_id':apk['_id']},
                        {'$set':{
                            'name':name,
                            'uid':self.session.uid,
                            'cid':cid,
                            'descr':descr,
                            'thumbid':thumbid,
                            'originids':originids,
                            'author':author,
                            'origin':origin,
                            }
                            }
                        )
                return self.redirect('/theme/home/d')
        else:
            if ctype==1:
                live_mongo.apk.update(
                        {'_id':apk['_id']},
                        {'$set':{
                            'name':name,
                            'uid':self.session.uid,
                            'cid':cid,
                            'descr':descr,
                            'author':author,
                            'origin':origin,
                            }
                            }
                        )
                return self.redirect('/live/home/%s/0' % str(cid))
            else:
                theme_mongo.apk.update(
                        {'_id':apk['_id']},
                        {'$set':{
                            'name':name,
                            'uid':self.session.uid,
                            'cid':cid,
                            'descr':descr,
                            'author':author,
                            'origin':origin,
                            }
                            }
                        )
                return self.redirect('/theme/home/d')



class DeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,apkid):
        print 'delete handler'
        ctype = self.get_argument("type",default=1)
        ctype = int(ctype)
        try:
            pid = objectid.ObjectId(apkid)
            if ctype==1:
                apkItem = live_mongo.apk.find_one({'_id':pid})
            else:
                apkItem = theme_mongo.apk.find_one({'_id':pid})
            if not apkItem:
                raise
        except:
            raise tornado.web.HTTPErro(404)

        live_mongo.apk2tag.remove({'apkid': pid})
        live_mongo.private.remove({'apkid': pid})
        live_mongo.apk.remove({'_id':pid})

        return self.redirect("/live/home/%s/0" % apkItem['cid'])


class ShowHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, apkid):
        ctype = self.get_argument("type", default=1)

        try:
            ctype = int(ctype)
        except:
            ctype = 1

        try:
            pid = objectid.ObjectId(apkid)
            if ctype==1:
                apkItem = live_mongo.apk.find_one({'_id':pid})
            else:
                apkItem = theme_mongo.apk.find_one({'_id':pid})

            if not apkItem:
                raise
        except:
            raise tornado.web.HTTPErro(404)

        return self.render("show.html",
                apk=apkItem,
                type=ctype,
                )

