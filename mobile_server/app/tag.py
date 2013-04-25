#!/usr/bin/env python
#-*- coding: utf-8 -*-

import re
import urllib
import base64
import datetime
import tornado
from db import mongo
from pymongo import DESCENDING, ASCENDING
from bson import objectid
from libs import BaseHandler
import json


class TagAddHandler(BaseHandler):
    invalid_chars = ['/', '\\', ':', '?', '*', '"', '<', '.',
            '>', '&', '(', ')', '@','{', '}','%']

    meanness_chars = '1234567890qwertyuiopasdfghjklzxcvbnm'

    def validates(self,name):
        p = re.compile('.{2,15}$')
        return p.match(name)

    def check_user_taglog(self, imgid, name, ref):
        if mongo.img2tag.find_one({
            'imgid': imgid,
            'name': name,
            }):
            self.flash('标签重复啦，换一个吧')
            return self.redirect(ref)

   # @tornado.web.authenticated
    def get(self):
        name = self.get_argument('name',default=None)
        _imgid = self.get_argument('imgid',default=None)
       # _ref = self.get_argument('ref',default=None)

        name = name.strip()
        ref = None
     #   if _ref:
     #       ref=urllib.unquote(_ref)
     #   else:
     #       ref='/paperDetail'
        message = '顶标签成功'
        code = 0
        callback = self.get_argument('jsoncallback',default=None)
        if not callback:
            return
        if not name.strip():
            message='名字不合适'
            code = -1
            self._buffer = json.dumps({'code':code,'resp':message})
            self._buffer = "%s(%s)" % (callback,self._buffer)
            return self.write(self._buffer)

        uid = self.session.uid

        imgid = None
        try:
            imgid = objectid.ObjectId(_imgid)
            img = mongo.image.find_one({'_id': imgid})
            if not img: raise
        except:
            message='图片不存在'
            code = -1
            self._buffer = json.dumps({'code':code,'resp':message})
            self._buffer = "%s(%s)" % (callback,self._buffer)
            return self.write(self._buffer)

        tag = mongo.tag.find_one({'name': name})
        if not tag:
            message='标签不存在'
            code = -1
            self._buffer = json.dumps({'code':code,'resp':message})
            self._buffer = "%s(%s)" % (callback,self._buffer)
            return self.write(self._buffer)
        if mongo.img2tag.find_one({
            'uids': uid,
            'imgid': imgid,
            'name': name
            }):
            message='已顶过该标签'
            code = -1
            self._buffer = json.dumps({'code':code,'resp':message})
            self._buffer = "%s(%s)" % (callback,self._buffer)
            return self.write(self._buffer)

        img2tag = mongo.img2tag.find_one({
            'imgid': imgid,
            'name': name
            })
        if img2tag:
            mongo.img2tag.update(
                    {'_id': img2tag['_id']},
                    {'$inc': {'num': 1}, '$push': {'uids': uid}}
                    )
        else:
            message='来路不明的标签添加'
            code = -1
            self._buffer = json.dumps({'code':code,'resp':message})
            self._buffer = "%s(%s)" % (callback,self._buffer)
            return self.write(self._buffer)

        log = mongo.taglog.find_one({'name': name})
        if log:
            log['count'] += 1
            mongo.taglog.save(log)
        else:
            mongo.taglog.insert({
                'uid': uid,
                'name': name,
                'count': 0,
                'atime': datetime.datetime.now()
                })

        self._buffer = json.dumps({'code':code,'resp':message})
        self._buffer = "%s(%s)" % (callback,self._buffer)
        return self.write(self._buffer)

    def filter_deny(self, tag):
        for i in mongo.fkilter.find():
            if i['keyword'] in tag:
                return True

        return False

    def post(self):
        name = self.get_argument('name',default=None)
        _imgid = self.get_argument('imgid',default=None)
        _ref = self.get_argument('ref',default=None)
        #_ref = ref_raw
        #_ref = base64.decodestring(ref_raw)
    	ref = None
        self.session.show_msg = None
        if _ref:
            ref=urllib.unquote(_ref)
        else:
            ref='/paperDetail'

        if not self.session.uid:
            return self.redirect("/login?next="+_ref+"#t0:2", permanent=False)

        if not name :
            self.session.show_msg ="标签不能为空"
            return self.redirect(ref)

        if not self.validates(name):
            self.session.show_msg ="标签长度应为2-15位"
            return self.redirect(ref, permanent=False)
        if not self.session.uid:
            return self.redirect("/login?next="+urllib.quote(_ref), permanent=False)

        if not self.session.super and name.find('_')==0:
            self.session.show_msg ="标签含有非法字符"
            return self.redirect(ref)

        for i in self.invalid_chars:
            if i in name:
                self.session.show_msg ="标签含有非法字符"
                return self.redirect(ref)

        name = name.strip()
        if len(name) == 1 and name in self.meanness_chars:
            self.session.show_msg ="标签太短"
            return self.redirect(ref)

        if self.filter_deny(name):
            self.session.show_msg = "标签含有违禁字符，请重新填写"
            return self.redirect(ref)

        imgid = None
        try:
            imgid = objectid.ObjectId(_imgid)
        except:
            self.session.show_msg ="图片错误"
            return self.redirect(ref)

        img2tag = mongo.img2tag.find_one({'name': name, 'imgid': imgid})
        if img2tag:
            self.session.show_msg ="标签重复啦，换一个吧"
            return self.redirect(ref)
        else:
            mongo.img2tag.insert({
                'name': name,
                'imgid': imgid,
                'uids': [self.session.uid],
                'num': 1,
                'atime': datetime.datetime.now()
                })

        tag = mongo.tag.find_one({'name': name})
        if not tag:
            tid = mongo.tag.insert({
                'name': name,
                'descr': '',
                'uid': self.session.uid,
                'rank': 1,
                'atime': datetime.datetime.now()
                }, safe=True)

        else:
            mongo.tag.update(
                    {'_id': tag['_id']},
                    {'$inc': {'rank': 1}}
                    )

        # add tag increase 2 point
        mongo.user.update(
                {'_id': self.session.uid},
                {'$inc': {'rank': 2}}
                        )
        self.session.show_msg ="添加标签成功"
        if not self.session.super:
            log = mongo.taglog.find_one({'name': name})
            if log:
                log['count'] += 1
                mongo.taglog.save(log)
            else:
                mongo.taglog.insert({
                    'uid': self.session.uid,
                    'name': name,
                    'count': 0,
                    'atime': datetime.datetime.now()
                    })
        return self.redirect(ref)

class TagFindHandler(BaseHandler):
    limit = 30

    def get(self):
        name = self.get_argument('name',default=None)
        _offset = self.get_argument('offset',default=None)
        _page = self.get_argument('page',default=None)
        uri = self.get_argument('uri',default=None)

        try:
            name = name.strip()
        except AttributeError:
            name = None
        tag = None
        try:
            tag = mongo.tag.find_one({'name': name})
            if not tag:
                raise
        except:
            self.flash("标签不存在")
            return self.notfound()

        if tag['name'].find('_')==0:
            tag['name'] = tag['name'][1:]

        offset = 0
        try:
            offset = int(_offset)
        except:
            pass

        page = 0
        try:
            page = int(page)
            page -= 1
        except:
            pass

        if page > 0:
            offset = page * self.limit

        uid = None
        try:
            uid = objectid.ObjectId(tag['uid'])
        except:
            self.flash("标签未知错误")
            return self.notfound()

        creater = mongo.user.find_one({'_id': uid})
        uri='/'
        if(uri==None):
            uri=self.request.uri
        return self.render("findtag.html",
                creater=creater,
                tag=tag,
                context=self.context,
                name=name,
                skip=offset,
                uri_quote=urllib.quote(uri),
                uri=uri,
                )

class MoreTagFindHandler(BaseHandler):
    limit = 18
    firstload_limit = 18

    def get(self):
        name = self.get_argument('name',default=None)
        _offset = self.get_argument('skip',default=None)
        _page = self.get_argument('page',default=None)

        try:
            name = name.strip()
        except AttributeError:
            name = None

        tag = None
        try:
            tag = mongo.tag.find_one({'name': name})
            if not tag:
                raise
        except:
            self.flash("标签不存在")
            return self.notfound()

        offset = 0
        try:
            offset = int(_offset)
        except:
            pass

        page = 0
        try:
            page = int(_page)
            page -= 1
        except:
            pass

        if page > 0:
            offset = page * self.limit

        uid = None
        try:
            uid = objectid.ObjectId(tag['uid'])
        except:
            self.flash("标签未知错误")
            return self.notfound()

        creater = mongo.user.find_one({'_id': uid})

        if offset == 0:
            img2tags = mongo.img2tag.find({'name': name},
                    limit=self.firstload_limit, skip=offset).sort('atime', DESCENDING)
        else:
            img2tags = mongo.img2tag.find({'name': name},
                    limit=self.limit, skip=offset).sort('atime', DESCENDING)
        length = img2tags.count()
        code = 0
        if length>self.limit+offset:
            code=1
        imgids = [i['imgid'] for i in img2tags]
        images = []
        for k, i in enumerate(imgids):
            img = mongo.image.find_one({'_id': i, 'process': True})
            if not img:
                length = length - 1
                continue

            t = img['atime'].strftime("%y/%m/%d")

            images.append({
                'id': img['_id'],
                'fobjs': img['fobjs'],
                'thumb_fobj': img['thumb_fobj'],
                'nickname': img['nickname'],
                'rank': img['rank'],
                'offset': offset + k,
                'atime': t
                })


        front, end, page, total = self.split_page(length, offset, self.limit)

        tail = (length / self.limit) * self.limit
        if tail < 0: tail = 0

        morefindtagpaper = []

        net = self.session.net
        for i in images:
            if not self.session.hd:
                morefindtagpaper.append({
                    'imgid':str(i['id']),
                    'image':i['thumb_fobj'],
                    'offset':i['offset'],
                    'act':'cate'
                    })
            elif net == 'pc':
                morefindtagpaper.append({
                    'imgid':str(i['id']),
                    'image':i['fobjs']['640x480'],
                    'offset':i['offset'],
                    'act':'cate'
                    })
            else: #if net == 'wifi':
                morefindtagpaper.append({
                    'imgid':str(i['id']),
                    'image':i['fobjs']['160x120'],
                    'offset':i['offset'],
                    'act':'cate'
                    })
        self._buffer = json.dumps({'code':code, 'resp': morefindtagpaper})
        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)

        self.write(self._buffer)



class TagpaperDetailHandler(BaseHandler):

    def _get_tag_image(self, offset, name):
        previous_img = {}
        next_img = {}

        length = mongo.img2tag.find({'name': name}).count()
        if length == 0:
            return (previous_img, next_img)

        if offset != 0:
            img2tags = mongo.img2tag.find({'name': name},
                    limit=1, skip=offset-1).sort('atime', DESCENDING)
            previous_img['imgid'] = img2tags[0]['imgid']
            previous_img['offset'] = offset - 1

        if offset < length -1:
            img2tags = mongo.img2tag.find({'name': name},
                    limit=1, skip=offset+1).sort('atime', DESCENDING)
            next_img['imgid'] = img2tags[0]['imgid']
            next_img['offset'] = offset + 1

        return (previous_img, next_img)

    def  getoffset(self,pre, nex):
        offset = 0
        if pre:
            offset = (pre['offset']+1) - (pre['offset']+1) % 15;
        elif nex:
            offset = (nex['offset']+1) - (nex['offset']+1) % 15;
        return offset

    def get(self):

        _imgid = self.get_argument('imgid',default=None)
        _offset = self.get_argument('offset',default=None)
        _name = self.get_argument('name',default=None)
        referer = self.get_argument('uri',default=None)

        try:
            name = _name.strip()
        except AttributeError:
            name = None

        imgid = None
        image = None
        try:
            imgid = objectid.ObjectId(_imgid)
            image = mongo.image.find_one({'_id': imgid, 'process': True})
            if not image:
                raise
        except:
            self.flash("抱歉，您所察看的图片不存在")
            return self.notfound()

        mongo.image.update({'_id': imgid}, {'$inc': {'views': 1}})

        owner = None
        try:
            owner = mongo.user.find_one({'_id': image['uid']})
        except:
            pass

        offset = 0
        try:
            offset = int(_offset)
        except:
            pass

        previous_img, next_img = {}, {}

        previous_img, next_img = self._get_tag_image(offset, name)

        dir = mongo.dir.find_one({'_id': image['dirid']})
        if dir:
            path_name = dir['rname']
        else:
            path_name = None

        private = False
        if self.session.login == True and mongo.private.find_one({
                'uid': self.session.uid,
                'imgid': imgid}):
                private = True
        tags = mongo.img2tag.find({'imgid': imgid}).sort('num', DESCENDING)
        tags =  [i for i in tags]
        offset = self.getoffset(previous_img,next_img)

        showmsg = self.session.show_msg
        self.session.show_msg = None
        self.render("tagpaper_detail.html",
                imgid = _imgid,
                private = private,
                message = showmsg,
                tags = tags,
                image = image,
                owner = owner,
                path_name = path_name,
                previous_img = previous_img,
                next_img = next_img,
                name = _name,
                net = self.session.net,
                reso = self.session.reso,
                context=self.context,
                uri =urllib.quote(self.request.uri),
                offset = offset,
                super = self.session.super,
                login = self.session.login,
                height = self.session.height,
                width = self.session.width,
                id = self.session.uid,
               # referer=urllib.quote(referer),
                )


