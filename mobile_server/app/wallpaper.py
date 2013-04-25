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
#import wallpaper as wp
from libs import BaseHandler
import json

class CategoryHandler(BaseHandler):
    def get(self):

        path = self.request.uri
        if not path and self.session.login:
            return self.redirect("/login")

        categorys = mongo.category.find().sort('rank', ASCENDING)
        cates = []
        for i in categorys:
            image = mongo.image.find_one({'_id': i['cover'], 'process': True})

            thumbid = image['fobjs']['300x225']
            if not self.session.hd:
                thumbid = image['fobjs']['160x120']
            elif self.session.net=='pc':
                thumbid = image['fobjs']['640x480']

            cates.append({
                'id': str(i['_id']),
                'rname': i['rname'],
                'name': i['name'],
                'thumbid': str(thumbid)
                })
        _buffer = json.dumps({'code':0, 'resp':cates})
        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            _buffer = "%s(%s)" % (callback,_buffer)
        self.write(_buffer)

class DirHandler(BaseHandler):

    limit = 10

    def get(self):
        _fid = self.get_argument('fid',default=None)
        _oid = self.get_argument('oid',default=None)

        if _fid:
            user = None
            try:
                fid= objectid.ObjectId(_fid)
                user = mongo.user.find_one({'_id': fid})
                if not user:
                    raise
            except:
                self.flash('用户不存在')
                raise self.notfound()
        elif _oid:
            user = None
            try:
                oid = objectid.ObjectId(_oid)
                user = mongo.user.find_one({'_id': oid})
                if not user:
                    raise
            except:
                self.flash('用户不存在')
                raise self.notfound()

        self.render("paper_zhuanji.html",
                fid = _fid,
                oid = _oid,
                skip = 0,
                context=self.context,
                )



class MoreDirHandler(BaseHandler):

    limit = 10

    def get_all(self, offset):

        dirs = []
        _dirs = mongo.dir.find({}, skip=offset, limit=self.limit).sort('follownum', DESCENDING)
        loseCode=0
        for i in _dirs:
            images = mongo.image.find({'dirid': i['_id']}, limit=1).sort('atime', DESCENDING)

            try:
                img = images[0]
            except:
                img = None

            if (str(i['_id']) == '4efdc8fd05697965ec00030d' or str(i['_id']) == '4efec81d0569792b3100001a') and self.session.channel == 'jifeng':
                loseCode += 1
                continue

            if str(i['_id']) == '4e4d74e805697913c8000000':
                loseCode += 1
                continue

            dirs.append({
                'dirid':str(i['_id']),
                'image':img['thumb_fobj'],
                'rname':i['rname'],
                'descr':i['descr'],
                'follow_num':str(i['follownum']),
                })

        return dirs, _dirs.count(),loseCode


    def get(self):

        _offset = self.get_argument('skip',default=None)

        offset = 0
        try:
            offset = int(_offset)
        except:
            pass

        moredirs = []
        loseCode=0
        moredirs, length, loseCode = self.get_all(offset)
        front, end, page, total = self.split_page(length, offset, self.limit)
        tail = (length / self.limit) * self.limit
        if tail < 0: tail = 0

        self._buffer = json.dumps({'code':loseCode, 'resp': moredirs})
        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)

        self.write(self._buffer)

class CategoryShowHandler(BaseHandler):
    limit = 30
    def get(self):
        order = self.get_argument('order',default=None)
        _offset = self.get_argument('offset',default=0)
        _cid = self.get_argument('cid',default=None)
        _page = self.get_argument('page',default=None)
        if order not in ('rank', 'date'):
            order = 'date'

        cid = None
        try:
            cid = objectid.ObjectId(_cid)
            category=mongo.category.find_one({'_id':cid})
            if not category:
                raise
        except:
            return tornado.web.HTTPError(404)

        self.render("paper_category_list.html",
                order = order,
                cateid = cid,
                skip=_offset,
                net = self.session.net,
                context=self.context,
                category=category,
                )

class MoreCateShowHandler(BaseHandler):
    limit = 18
    firstload_limit = 18
    def get(self):
        order = self.get_argument('order',default=None)
        _offset = self.get_argument('skip',default=0)
        _cid = self.get_argument('cateid',default=None)
        _page = self.get_argument('page',default=None)

        if order not in ('rank', 'date'):
            order = 'date'

        offset = 0
        try:
            offset = int(_offset)
        except:
            pass
        if offset>0 and order=='date':
            offset = offset-1
        begin=datetime.datetime.now()
        end = begin-datetime.timedelta(days=180)

        cid = None
        try:
            cid = objectid.ObjectId(_cid)
        except:
            raise
        if order == 'date':
            if offset == 0:
                images = mongo.image.find(
                        {'cid': cid, 'process': True}, limit=self.firstload_limit-1, skip=offset
                        ).sort('atime', DESCENDING)
            else:
                images = mongo.image.find(
                        {'cid': cid, 'process': True}, limit=self.limit, skip=offset
                        ).sort('atime', DESCENDING)
        elif order == 'rank':
            if offset == 0:
                images = mongo.image.find(
                        {'cid': cid, 'process': True, 'atime': {'$gt': end}}, limit=self.firstload_limit, skip=offset
                        ).sort('rank', DESCENDING)
            else:
                images = mongo.image.find(
                        {'cid': cid, 'process': True, 'atime': {'$gt': end}}, limit=self.limit, skip=offset
                        ).sort('rank', DESCENDING)

        imgs = []
        for i in images:
            if not self.session.hd:
                netimg = str(i['thumb_fobj'])
            elif self.session.net=='pc':
                netimg = str(i['fobjs']['640x480'])
            else: # self.session.net=='wifi':
                netimg = str(i['fobjs']['160x120'])
            imgs.append({
                    'src':netimg,
                    'id':str(i['_id'])
                    })
            offset=offset+1
            if offset==7 and order=='date':
                category=mongo.category.find_one({'_id':cid})
                midimage = mongo.image.find_one({'_id': category['cover'], 'process': True})
                if not self.session.hd:
                    netimg = str(midimage['thumb_fobj'])
                elif self.session.net=='pc':
                    netimg = str(midimage['fobjs']['640x480'])
                else: # self.session.net=='wifi':
                    netimg = str(midimage['fobjs']['160x120'])
                imgs.append({
                    'src':netimg,
                    'id':str(midimage['_id'])
                    })


        self._buffer = json.dumps({'code':0, 'resp':imgs})
        callback = self.get_argument('jsoncallback', default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)
        self.write(self._buffer)


class DirShowHandler(BaseHandler):

    limit = 30

    def get(self):

        order = self.get_argument('order',default=None)
        _offset = self.get_argument('offset',default=0)
        path = self.get_argument('path',default=None)
        _uid = self.get_argument('uid',default=None)
        _page = self.get_argument('page',default=None)

        if order not in ('rank', 'date'):
            order = 'date'

        if _uid == None and path == None:
            path = 'all'


        dir = None
        uid = None
        try:
            uid = objectid.ObjectId(_uid)
        except:
            pass

        dirid = None
        try:
            dirid = objectid.ObjectId(path)
            dir = mongo.dir.find_one({'_id': dirid})
            if not dir: raise
        except:
            self.flash("专辑不存在")
            return self.notfound()

        follow = False
        if self.session.login:
            if mongo.followdir.find_one({'dirid': dirid, 'uid':self.session.uid}):
                follow = True

        dir['follow'] = follow

        user = mongo.user.find_one({'_id': dir['uid']})
        self.render("paper_zhuanji_list.html",
                context=self.context,
                order = order,
                dir = dir,
                path = path,
                uid = _uid,
                net = self.session.net,
                user = user,
                id = self.session.uid,
                uri =self.request.uri,
                skip=_offset,
                )


class MoreDirShowHandler(BaseHandler):

    limit = 18
    firstload_limit = 18

    def _get_path_image(self, dirid, offset, order):
        images = []
        if order == 'date':
            if offset == 0:
                images = mongo.image.find(
                        {'dirid': dirid, 'process': True}, limit=self.firstload_limit, skip=offset
                        ).sort('atime', DESCENDING)
            else:
                images = mongo.image.find(
                        {'dirid': dirid, 'process': True}, limit=self.limit, skip=offset
                        ).sort('atime', DESCENDING)
        elif order == 'rank':
            if offset == 0:
                images = mongo.image.find(
                        {'dirid': dirid, 'process': True}, limit=self.firstload_limit, skip=offset
                        ).sort('rank', DESCENDING)
            else:
                images = mongo.image.find(
                        {'dirid': dirid, 'process': True}, limit=self.limit, skip=offset
                        ).sort('rank', DESCENDING)
        return images


    def get(self):
        path = self.get_argument('path',default=None)
        order = self.get_argument("order",default=None)
        offset = self.get_argument("skip",default=0)

        try:
            offset = int(offset)
        except:
            pass

        if order not in ('rank', 'date'):
            order = 'date'

        dirid = None
        try:
            dirid = objectid.ObjectId(path)
            dir = mongo.dir.find_one({'_id': dirid})
            if not dir: raise
        except:
            self.flash("专辑不存在")
            return self.notfound()

        images = self._get_path_image(dirid, offset, order)

        imgs = []
        moredirpaper = []
        net = self.session.net
        for k, i in enumerate(images):
            if not self.session.hd:
                moredirpaper.append({
                    'imgid':str(i['_id']),
                    'image':i['thumb_fobj'],
                    'offset':offset+k,
                    'act':'cate',
                    'order':order
                    })
            elif net == 'pc':
                moredirpaper.append({
                    'imgid':str(i['_id']),
                    'image':i['fobjs']['640x480'],
                    'offset':offset+k,
                    'act':'cate',
                    'order':order
                    })
            else: #if net == 'wifi':
                moredirpaper.append({
                    'imgid':str(i['_id']),
                    'image':i['fobjs']['160x120'],
                    'offset':offset+k,
                    'act':'cate',
                    'order':order
                    })

        if images:
            length = images.count()
        else:
            length = 0

        front, end, page, total = self.split_page(length, offset, self.limit)

        tail = (length / self.limit) * self.limit
        if tail < 0: tail = 0

        self._buffer = json.dumps({'code':0, 'resp': moredirpaper,})
        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)

        self.write(self._buffer)


class DetailHandler(BaseHandler):
    """
    vtag = form.regexp(r".{1,6}$", '长度为1-6')
    tagform = form.Form(
            form.Textbox('name', vtag, description="新标签"),
            form.Hidden('imgid'),
            form.Hidden('ref')
            )
"""
    def _get_owner_image(self, offset, oid):
        previous_img = {}
        next_img = {}

        length = mongo.image.find({'uid': oid, 'process': True}).count()
        if length == 0:
            return (previous_img, next_img)

        if offset != 0:
            image = mongo.image.find({'uid': oid, 'process': True},
                    skip=offset-1, limit=1).sort('atime', DESCENDING)
            previous_img['imgid'] = image[0]['_id']
            previous_img['offset'] = offset-1
        if offset < length -1:
            image = mongo.image.find({'uid': oid, 'process': True},
                    skip=offset+1, limit=1).sort('atime', DESCENDING)
            next_img['imgid'] = image[0]['_id']
            next_img['offset'] = offset+1

        return (previous_img, next_img)

    def _get_settinglog_image(self, offset, _uid):
        previous_img = {}
        next_img = {}

        uid = None
        try:
            uid = objectid.ObjectId(_uid)
        except:
            self.flash('用户不存在')
            raise self.notfound()

        length = mongo.setting_log.find({'uid': _uid}).count()
        if length == 0:
            return (previous_img, next_img)

        if offset != 0:
            private = mongo.setting_log.find({'uid': _uid},
                    skip=offset-1, limit=1).sort('atime', DESCENDING)
            previous_img['imgid'] = private[0]['imgid']
            previous_img['offset'] = offset-1

        if offset < length -1 :
            private = mongo.setting_log.find({'uid': _uid},
                    skip=offset+1, limit=1).sort('atime', DESCENDING)
            next_img['imgid'] = private[0]['imgid']
            next_img['offset'] = offset + 1

        return (previous_img, next_img)

    def _get_private_image(self, offset, _uid):
        previous_img = {}
        next_img = {}

        uid = None
        try:
            uid = objectid.ObjectId(_uid)
        except:
            self.flash('用户不存在')
            raise self.notfound()

        length = mongo.private.find({'uid': uid}).count()
        if length == 0:
            return (previous_img, next_img)

        if offset != 0:
            private = mongo.private.find({'uid': uid},
                    skip=offset-1, limit=1).sort('atime', DESCENDING)
            previous_img['imgid'] = private[0]['imgid']
            previous_img['offset'] = offset-1

        if offset < length -1 :
            private = mongo.private.find({'uid': uid},
                    skip=offset+1, limit=1).sort('atime', DESCENDING)
            next_img['imgid'] = private[0]['imgid']
            next_img['offset'] = offset + 1

        return (previous_img, next_img)

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

    def _get_cate_image(self, offset, cid, order):
        previous_img = {}
        next_img = {}
        begin=datetime.datetime.now()
        end = begin-datetime.timedelta(days=180)

        length = mongo.image.find({'cid': cid, 'process': True}).count()
        if length == 0:
            return (previous_img, next_img)

        if offset != 0:
            if order == 'date':
                if offset==8:
                    category=mongo.category.find_one({'_id':cid})
                    images = mongo.image.find({'_id': category['cover'], 'process': True})
                else:
                    toffset=offset
                    if offset>8:
                        toffset = offset-1
                    images = mongo.image.find(
                            {'cid': cid, 'process': True},
                            limit=1, skip=toffset-1
                            ).sort('atime', DESCENDING)
            elif order == 'rank':
                images = mongo.image.find(
                        {'cid': cid, 'process': True, 'atime': {'$gt': end}},
                        limit=1, skip=offset-1
                        ).sort('rank', DESCENDING)
            previous_img['imgid'] = images[0]['_id']
            previous_img['offset'] = offset - 1

        if offset < length-1:
            if order == 'date':
                if offset==6:
                    category=mongo.category.find_one({'_id':cid})
                    images = mongo.image.find({'_id': category['cover'], 'process': True})
                else:
                    toffset=offset
                    if offset>6:
                        toffset=offset-1
                    images = mongo.image.find(
                            {'cid': cid, 'process': True},
                            limit=1, skip=toffset+1
                            ).sort('atime', DESCENDING)
            elif order == 'rank':
                images = mongo.image.find(
                        {'cid': cid, 'process': True, 'atime': {'$gt': end}},
                        limit=1, skip=offset+1
                        ).sort('rank', DESCENDING)
            next_img['imgid'] = images[0]['_id']
            next_img['offset'] = offset + 1

        return (previous_img, next_img)

    def _get_dir_image(self, offset, path, dirid, order):
        previous_img = {}
        next_img = {}

        if order not in ('rank', 'date'):
            order = 'date'

        if path == 'all':
            length = mongo.image.find({'process': True}).count()
        else:
            length = mongo.image.find({'dirid': dirid, 'process': True}).count()

        if length == 0:
            return (previous_img, next_img)

        if offset != 0:
            if path == 'all':
                if order == 'date':
                    images = mongo.image.find(
                            {'process': True},
                            limit=1, skip=offset-1
                            ).sort('atime', DESCENDING)
                elif order == 'rank':
                    images = mongo.image.find(
                            {'process': True},
                            limit=1, skip=offset-1
                            ).sort('rank', DESCENDING)
            else:
                if order == 'date':
                    images = mongo.image.find(
                            {'dirid': dirid, 'process': True}, limit=1, skip=offset-1
                            ).sort('atime', DESCENDING)
                elif order == 'rank':
                    images = mongo.image.find(
                            {'dirid': dirid, 'process': True}, limit=1, skip=offset-1
                            ).sort('rank', DESCENDING)
            previous_img['imgid'] = images[0]['_id']
            previous_img['offset'] = offset - 1

        if offset < length-1:
            if path == 'all':
                if order == 'date':
                    images = mongo.image.find(
                            {'process': True},
                            limit=1, skip=offset+1
                            ).sort('atime', DESCENDING)
                elif order == 'rank':
                    images = mongo.image.find(
                            {'process': True},
                            limit=1, skip=offset+1
                            ).sort('rank', DESCENDING)
            else:
                if order == 'date':
                    images = mongo.image.find(
                            {'dirid': dirid, 'process': True}, limit=1, skip=offset+1
                            ).sort('atime', DESCENDING)
                elif order == 'rank':
                    images = mongo.image.find(
                            {'dirid': dirid, 'process': True}, limit=1, skip=offset+1
                            ).sort('rank', DESCENDING)

            next_img['imgid'] = images[0]['_id']
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
        act = self.get_argument('act',default=None)
        order = self.get_argument('order',default=None)
        path = self.get_argument('path',default=None)
        uid = self.get_argument('uid',default=None)
        _name = self.get_argument('name',default=None)
        oid = self.get_argument('oid',default=None)
        showmsg = self.session.show_msg
        self.session.show_msg = None
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

        if act == 'private':
            previous_img, next_img = self._get_private_image(offset, uid)
        elif act == 'dir':
            previous_img, next_img = self._get_dir_image(offset, path, image['dirid'], order)
        elif act == 'tag':
            previous_img, next_img = self._get_tag_image(offset, name)
        elif act == 'owner':
            previous_img, next_img = self._get_owner_image(offset, objectid.ObjectId(oid))
        elif act == 'cate':
            previous_img, next_img = self._get_cate_image(offset, image['cid'], order)
        elif act == 'setlog':
            previous_img, next_img = self._get_settinglog_image(offset, uid)
        else:
            pass

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
        self.render("paper_detail.html",
                imgid = _imgid,
                private = private,
                tags = tags,
                message = showmsg,
                image = image,
                owner = owner,
                path_name = path_name,
                previous_img = previous_img,
                next_img = next_img,
                act = act,
                path = path,
                order = order,
                uid = uid,
                name = _name,
                oid = oid,
                net = self.session.net,
                context=self.context,
                uri =urllib.quote(self.request.uri),
                offset = offset,
                super = self.session.super,
                login = self.session.login,
                height = self.session.height,
                width = self.session.width,
                id = self.session.uid,
                reso = self.session.reso,
                )



class SettingWallpaperHandler(BaseHandler):
    #@tornado.web.authenticated
    def get(self):
        _uid = self.get_argument('uid',default=None)
        _imgid = self.get_argument('imgid',default=None)
        reso = self.get_argument('reso',default=None)

        uid = None
        image = None
        try:
            imgid = objectid.ObjectId(_imgid)
            image = mongo.image.find_one({'_id': imgid})
            if not image:
                raise
        except:
            raise self.notfound()

        # setting wallpaper add 2 point
        if _uid != None:
            user = None
            try:
                uid = objectid.ObjectId(_uid)
                user = mongo.user.find_one({'_id': uid})
                if not user:
                    raise
            except:
                pass
            else:
                if not mongo.setting_log.find_one({
                    'uid': _uid,
                    'imgid': imgid
                    }):
                    mongo.user.update(
                            {'_id': uid},
                            {'$inc': {'rank': 1}}
                            )

                mongo.user.update(
                        {'_id': uid},
                        {'$set': {
                            'wallpaper': imgid,
                            'wallpaper_setime': datetime.datetime.now()
                            }}
                        )

            mongo.setting_log.insert({
                'uid': _uid,
                'imgid': imgid,
                'atime': datetime.datetime.now()
                })

        mongo.image.update(
                {'_id': imgid },
                {'$set': {'rank': image['rank'] + 1}}
                )

        key = None
        try:
            image['fobjs'][reso]
            key = reso
        except KeyError:
            try:
                key = '1280x960'
                image['fobjs'][key]
            except KeyError:
                key = '960x800'

        _objid = objectid.ObjectId(image['fobjs'][key])

        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition','attachment;filename="%s.jpg"' % _imgid)
        return mongo.imgfs.get(_objid).read()






