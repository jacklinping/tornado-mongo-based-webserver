#-*- coding: utf-8 -*-

import tornado
import json
import urllib
import datetime
import base64
from pymongo import DESCENDING, ASCENDING
from bson import objectid
from libs import BaseHandler
from db import mongo,live_mongo,theme_mongo

class PersonalHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = mongo.user.find_one({'_id': self.session.uid})

        try:
            if user['wallpaper']!=None:
                image=mongo.image.find_one({'_id': user['wallpaper']})
                recent_imgid=image['fobjs']['480x320']
            else:
                raise "no such image"
        except:
            image=mongo.image.find_one({'cid':objectid.ObjectId('4e4d610cdf714d2966000002')})
            recent_imgid=image['fobjs']['480x320']

        self.render("personal.html",
                context=self.context,
                user=user,
                recent_imgid=recent_imgid,
                )

class OtherProfileHandler(BaseHandler):
    def get(self,userid=None):
        try:
            uid = objectid.ObjectId(userid)
            user = mongo.user.find_one({'_id':uid})
            if not user:
                raise
        except:
            return self.notfound()

        if str(userid) == str(self.session.uid):
            try:
                if user['wallpaper']!=None:
                    image=mongo.image.find_one({'_id': user['wallpaper']})
                    recent_imgid=image['fobjs']['480x320']
                else:
                    raise
            except:
                image=mongo.image.find_one({'cid':objectid.ObjectId('4e4d610cdf714d2966000002')})
                recent_imgid=image['fobjs']['480x320']

            return self.render("personal.html",
                    context=self.context,
                    user=user,
                    recent_imgid=recent_imgid,
                    )
        else:
            try:
                if user['wallpaper']!=None:
                    image=mongo.image.find_one({'_id': user['wallpaper']})
                    recent_imgid=image['fobjs']['480x320']
                else:
                    raise
            except:
                image=mongo.image.find_one({'cid':objectid.ObjectId('4e4d610cdf714d2966000002')})
                recent_imgid=image['fobjs']['480x320']

            return self.render("otherprofile.html",
                    context=self.context,
                    user=user,
                    uid = userid,
                    recent_imgid=recent_imgid,
                    )

class EditHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = mongo.user.find_one({'_id': self.session.uid})
        self.render("change.html",
                context=self.context,
                message=None,
                user=user,
                )

    @tornado.web.authenticated
    def post(self):
        nickname = self.get_argument("name",default=None)
        gender = self.get_argument("sex",default=None)

        tmp = mongo.user.find_one({'nickname':nickname.strip()})
        if tmp and tmp['_id'] != self.session.uid:
            user = mongo.user.find_one({'_id': self.session.uid})
            return self.render("change.html",
                    context=self.context,
                    message='用户名已存在',
                    user=user,
                    )
        if gender:
            mongo.user.update({'_id': self.session.uid},
                {'$set':{
                    'nickname':nickname,
                    'gender':gender,
                    }}
                )
        else:
            mongo.user.update({'_id': self.session.uid},
                {'$set':{
                    'nickname':nickname,
                    }}
                )

        self.session.nickname = nickname
        self.redirect("/personal")

class FavorHandler(BaseHandler):
    def get(self,userid=None):
        if not userid:
            return self.notfound()
        try:
            userid = objectid.ObjectId(userid)
        except:
            return self.notfound()

        ppaper = mongo.private.find({'uid':userid},limit=1).sort('atime', DESCENDING)
        pcount = ppaper.count()
        curpaper=None

        if ppaper and pcount > 0:
            curpaper = mongo.image.find_one({'_id':ppaper[0]['imgid']})

        plive = live_mongo.private.find({'uid':userid},limit=1).sort('atime', DESCENDING)
        lcount = plive.count()
        curlive=None

        if plive and lcount > 0:
            curlive = live_mongo.apk.find_one({'_id':plive[0]['apkid']})

        referer = '/otherprofile/'+str(userid)
        if userid==self.session.uid:
            referer = '/personal'

        self.render("myfavor.html",
                context=self.context,
                referer = referer,
                userid=userid,
                papercount=pcount,
                livecount=lcount,
                curpaper=curpaper,
                curlive=curlive,
                )


class AttentionHandler(BaseHandler):
    def get(self,userid=None):
        if not userid:
            return self.notfound()

        skip = self.get_argument("skip",default=0)
        if not skip: skip =0
        else: skip = int(skip)
        referer = '/otherprofile/'+str(userid)
        if userid==str(self.session.uid):
            referer = '/personal'
        self.render("myattention.html",
                context=self.context,
                referer=referer,
                userid=userid,
                skip=skip,
                )

class MoreAttentionHandler(BaseHandler):
    limit = 10

    def _get_new_image_num(self, dirid, today):
        return mongo.image.find({
            'dirid': dirid,
            'atime': {'$gt': today}
            }).count()

    def _get_new_follower_num(self, dirid, today):
        return mongo.followdir.find({
            'dirid': dirid,
            'atime': {'$gt': today}
            }).count()

    def get_follow(self, user, offset):
        now = datetime.datetime.now()
        today = now - datetime.timedelta(
                hours=now.hour, minutes=now.minute, seconds=now.second
                )

        dirs = []
        follow = mongo.followdir.find({'uid': user['_id']}, skip=offset, limit=self.limit)
        for i in follow:
            images = mongo.image.find({'dirid': i['dirid']}, limit=1).sort('atime', DESCENDING)
            dir = mongo.dir.find_one({'_id': i['dirid']})
            if dir == None:
                continue

            try:
                img = images[0]
            except:
                img = None

            newimg_num = self._get_new_image_num(dir['_id'], today)

            dirs.append({
                '_id': dir['_id'],
                'uid': dir['uid'],
                'rname': dir['rname'],
                'descr': dir['descr'],
                'image': img,
                'newimg_num': newimg_num,
                'follow_num': dir['follownum'],
                })

        dirs.sort(key=lambda obj:obj.get('newimg_num'))
        dirs.reverse()
        return dirs, follow.count()

    def get_owner(self, user, offset):
        now = datetime.datetime.now()
        today = now - datetime.timedelta(
                hours=now.hour, minutes=now.minute, seconds=now.second
                )

        dirs = []
        _dirs = mongo.dir.find({'uid': user['_id']}, skip=offset, limit=self.limit).sort('follownum', DESCENDING)
        for i in _dirs:
            images = mongo.image.find({'dirid': i['_id']}, limit=1).sort('atime', DESCENDING)

            try:
                img = images[0]
            except:
                img = None

            new_follow = self._get_new_follower_num(i['_id'], today)

            dirs.append({
                '_id': i['_id'],
                'uid': i['uid'],
                'rname': i['rname'],
                'descr': i['descr'],
                'image': img,
                'follow_num': i['follownum'],
                'new_follow': new_follow
                })

        return dirs, _dirs.count()


    def get_all(self, offset):
        now = datetime.datetime.now()
        today = now - datetime.timedelta(
                hours=now.hour, minutes=now.minute, seconds=now.second
                )

        dirs = []
        _dirs = mongo.dir.find({}, skip=offset, limit=self.limit).sort('follownum', DESCENDING)
        for i in _dirs:
            images = mongo.image.find({'dirid': i['_id']}, limit=1).sort('atime', DESCENDING)

            try:
                img = images[0]
            except:
                img = None

            newimg_num = self._get_new_image_num(i['_id'], today)

            dirs.append({
                '_id': i['_id'],
                'uid': i['uid'],
                'rname': i['rname'],
                'descr': i['descr'],
                'image': img,
                'follow_num': i['follownum'],
                'newimg_num': newimg_num
                })

        return dirs, _dirs.count()


    def get(self):

        fid = self.get_argument("userid",default=None)
        _offset = self.get_argument("skip",default=0)

        _page = self.get_argument("page",default=None)

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

        if fid:
            user = None
            try:
                fid= objectid.ObjectId(fid)
                user = mongo.user.find_one({'_id': fid})
                if not user:
                    raise
            except:
                self.flash('用户不存在')
                return self.notfound()

            dirs, length = self.get_follow(user, offset)
        else:
            dirs, length = self.get_all(offset)

        front, end, page, total = self.split_page(length, offset, self.limit)
        tail = (length / self.limit) * self.limit
        if tail < 0: tail = 0

        attention = []
        for i in dirs:
            attention.append({
                'dirid':str(i['_id']),
                'image':i['image']['thumb_fobj'],
                'rname':i['rname'],
                'descr':i['descr'],
                'follow_num':str(i['follow_num']),
                'newimg_num':str(i['newimg_num']),
                })

        self._buffer = json.dumps({'code':0, 'resp': attention})
        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)

        self.write(self._buffer)

class UsedHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,userid=None):
        pass

class AlbumHandler(BaseHandler):
    def get(self,userid=None):
        if not userid:
            return self.notfound()

        skip = self.get_argument("skip",default=0)
        if not skip: skip =0
        else: skip = int(skip)
        referer = '/otherprofile/'+userid
        if userid==str(self.session.uid):
            referer = '/personal'
        self.render("myalbum.html",
                context=self.context,
                referer=referer,
                userid=userid,
                skip=skip,
                )

class MoreAlbumHandler(BaseHandler):

    limit = 10

    def _get_new_image_num(self, dirid, today):
        return mongo.image.find({
            'dirid': dirid,
            'atime': {'$gt': today}
            }).count()

    def _get_new_follower_num(self, dirid, today):
        return mongo.followdir.find({
            'dirid': dirid,
            'atime': {'$gt': today}
            }).count()


    def get_owner(self, user, offset):
        now = datetime.datetime.now()
        today = now - datetime.timedelta(
                hours=now.hour, minutes=now.minute, seconds=now.second
                )

        dirs = []
        _dirs = mongo.dir.find({'uid': user['_id']}, skip=offset, limit=self.limit).sort('follownum', DESCENDING)
        for i in _dirs:
            images = mongo.image.find({'dirid': i['_id']}, limit=1).sort('atime', DESCENDING)

            try:
                img = images[0]
            except:
                img = None

            new_follow = self._get_new_follower_num(i['_id'], today)

            dirs.append({
                '_id': i['_id'],
                'uid': i['uid'],
                'rname': i['rname'],
                'descr': i['descr'],
                'image': img,
                'follow_num': i['follownum'],
                'new_follow': new_follow
                })

        return dirs, _dirs.count()


    def get_all(self, offset):
        now = datetime.datetime.now()
        today = now - datetime.timedelta(
                hours=now.hour, minutes=now.minute, seconds=now.second
                )

        dirs = []
        _dirs = mongo.dir.find({}, skip=offset, limit=self.limit).sort('follownum', DESCENDING)
        for i in _dirs:
            images = mongo.image.find({'dirid': i['_id']}, limit=1).sort('atime', DESCENDING)

            try:
                img = images[0]
            except:
                img = None

            newimg_num = self._get_new_image_num(i['_id'], today)

            dirs.append({
                '_id': i['_id'],
                'uid': i['uid'],
                'rname': i['rname'],
                'descr': i['descr'],
                'image': img,
                'follow_num': i['follownum'],
                'newimg_num': newimg_num
                })

        return dirs, _dirs.count()


    def get(self):
        _offset = self.get_argument("skip",default=0)
        oid = self.get_argument("userid",default=None)
        _page = self.get_argument("page",default=None)

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

        if oid:
            user = None
            try:
                oid= objectid.ObjectId(oid)
                user = mongo.user.find_one({'_id': oid})
                if not user:
                    raise
            except:
                self.flash('用户不存在')
                return self.notfound()

            dirs, length = self.get_owner(user, offset)
        else:
            dirs, length = self.get_all(offset)

        front, end, page, total = self.split_page(length, offset, self.limit)
        tail = (length / self.limit) * self.limit
        if tail < 0: tail = 0
        album = []
        for i in dirs:
            album.append({
                'dirid':str(i['_id']),
                'image':i['image']['thumb_fobj'],
                'rname':i['rname'],
                'descr':i['descr'],
                'follow_num':str(i['follow_num']),
                'new_follow':str(i['new_follow']),
                })
        self._buffer = json.dumps({'code':0, 'resp': album})
        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)

        self.write(self._buffer)


class UploadHandler(BaseHandler):
    def get(self,userid=None):
        if not userid:
            return self.notfound()
        try:
            uid = objectid.ObjectId(userid)
        except:
            return self.notfound()

        skip = self.get_argument("skip",default=0)
        if not skip: skip =0
        else: skip = int(skip)
        referer = '/otherprofile/'+userid
        if userid==str(self.session.uid):
            referer = '/personal'
        self.render("myupload.html",
                context=self.context,
                referer=referer,
                skip=skip,
                userid=userid,
                )


class MoreUploadHandler(BaseHandler):
    limit = 18
    firstload_limit = 18

    def _get_all_image(self, offset, order):
        images = []
        if order == 'date':
            if offset == 0:
                images = mongo.image.find(
                        {'process': True},
                        limit=self.firstload_limit, skip=offset
                        ).sort('atime', DESCENDING)
            else:
                images = mongo.image.find(
                        {'process': True},
                        limit=self.limit, skip=offset
                        ).sort('atime', DESCENDING)
        elif order == 'rank':
            if offset == 0:
                images = mongo.image.find(
                        {'process': True},
                        limit=self.firstload_limit, skip=offset
                        ).sort('rank', DESCENDING)
            else:
                images = mongo.image.find(
                        {'process': True},
                        limit=self.limit, skip=offset
                        ).sort('rank', DESCENDING)

        return images

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

    def _get_user_image(self, uid, offset):
        images = []
        if offset == 0:
            images = mongo.image.find(
                    {'uid': uid, 'process': True}, limit=self.firstload_limit, skip=offset
                    ).sort('atime', DESCENDING)
        else:
            images = mongo.image.find(
                    {'uid': uid, 'process': True}, limit=self.limit, skip=offset
                    ).sort('atime', DESCENDING)
        return images

    def get(self):
        _offset = self.get_argument("skip",default=0)
        _uid = self.get_argument("userid",default=None)
        _page = self.get_argument("page",default=None)
        order = self.get_argument("order",default=None)
        path = self.get_argument("path",default=None)

        if order not in ('rank', 'date'):
            order = 'date'

        if _uid == None and path == None:
            path = 'all'

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

        dir = None

        uid = None
        try:
            uid = objectid.ObjectId(_uid)
        except:
            pass

        if _uid:
            images = self._get_user_image(uid, offset)

        elif path == 'all':
            images = self._get_all_image(offset, order)

        else:
            dirid = None
            try:
                dirid = objectid.ObjectId(path)
                dir = mongo.dir.find_one({'_id': dirid})
                if not dir: raise
            except:
                self.flash("分类不存在")
                return self.notfound()

            fids = mongo.followdir.find({'dirid': dirid}, limit=20).sort('atime', ASCENDING)
            followers = []
            for i in fids:
                user = mongo.user.find_one({'_id': i['uid']})
                if user: followers.append(user)

            dir['followers'] = followers
            dir['follower_num'] = fids.count()

            follow = False
            if self.session.login:
                if mongo.followdir.find_one({'dirid': dirid, 'uid': self.session.uid}):
                    follow = True
            dir['follow'] = follow

            images = self._get_path_image(dirid, offset, order)

        try:
            length = images.count()
        except:
            length = 0

        front, end, page, total = self.split_page(length, offset, self.limit)

        tail = (length / self.limit) * self.limit
        if tail < 0: tail = 0
        upload = []
        for k, i in enumerate(images):
            if not self.session.hd:
                upload.append({
                    'imgid':str(i['_id']),
                    'image':i['thumb_fobj'],
                    'offset':offset + k,
                    'act':'cate',
                    'order':order
                    })
            elif self.session.net == 'pc':
                upload.append({
                    'imgid':str(i['_id']),
                    'image':i['fobjs']['640x480'],
                    'offset':offset + k,
                    'act':'cate',
                    'order':order
                    })
            else: #if self.session.net == 'wifi':
                upload.append({
                    'imgid':str(i['_id']),
                    'image':i['fobjs']['160x120'],
                    'offset':offset + k,
                    'act':'cate',
                    'order':order
                    })
        self._buffer = json.dumps({'code':0, 'resp': upload,'userid':_uid})
        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)

        self.write(self._buffer)


class TagHandler(BaseHandler):
    def get(self,userid=None):
        try:
            uid = objectid.ObjectId(userid)
            tags = mongo.tag.find({'uid':uid}).sort('rank', DESCENDING)
            if not tags:
                raise
        except:
            return self.notfound()

        referer = '/otherprofile/'+userid
        if userid==str(self.session.uid):
            referer = '/personal'
        uri = urllib.quote(self.request.uri)
        self.render("mytag.html",
                context=self.context,
                referer=referer,
                tags=tags,
                uri=uri,
                )


class PaperFavorHandler(BaseHandler):
    def get(self,userid=None):
        if not userid:
            return self.notfound()

        isSelf=False
        if userid!=None and str(userid)==str(self.context['se'].uid):
            isSelf=True

        skip = self.get_argument("skip",default=0)
        if not skip: skip =0
        else: skip = int(skip)

        self.render("myfavorpaper.html",
                context=self.context,
                userid=userid,
                skip=skip,
                isSelf=isSelf,
                )

class MoreFavorPaperHandler(BaseHandler):
    limit = 18
    firstload_limit = 18
    def get(self):
        userid = self.get_argument("userid",default=None)
        skip = self.get_argument("skip",default=0)
        if not skip: skip=0
        else: skip=int(skip)
        try:
            uid = objectid.ObjectId(userid)
        except:
            return self.notfound()
        papers = []
        code = 0
        if skip == 0:
            private = mongo.private.find({'uid':uid},skip=skip,limit=self.firstload_limit).sort('atime',DESCENDING)
        else:
            private = mongo.private.find({'uid':uid},skip=skip,limit=self.limit).sort('atime',DESCENDING)
        for k, i in enumerate(private):
            img = mongo.image.find_one({'_id':i['imgid']})
            if not img:
                continue
            if not self.session.hd:
                papers.append({
                    '_id':str(img['_id']),
                    'cid': str(img['cid']),
                    'thumbid': str(img['thumb_fobj']),
                    })
            elif self.session.net == 'pc':
                papers.append({
                    '_id':str(img['_id']),
                    'cid': str(img['cid']),
                    'thumbid': str(img['fobjs']['640x480']),
                    })
            else: #if self.session.net == 'wifi':
                papers.append({
                    '_id':str(img['_id']),
                    'cid': str(img['cid']),
                    'thumbid': str(img['fobjs']['160x120']),
                    })
        if private.count()>skip+self.limit:
            code=1
        self._buffer = json.dumps({'code':code, 'resp': papers})
        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)

        self.write(self._buffer)

class LiveFavorHandler(BaseHandler):
    def get(self,userid=None):
        if not userid:
            return self.notfound()

        skip = self.get_argument("skip",default=0)
        if not skip: skip =0
        else: skip = int(skip)
        self.render("myfavorlive.html",
                context=self.context,
                userid=userid,
                skip=skip,
                )
class MoreFavorLiveHandler(BaseHandler):
    def get(self):
        limit = 9
        userid = self.get_argument("userid",default=None)
        skip = self.get_argument("skip",default=0)
        if not skip: skip=0
        else: skip=int(skip)
        try:
            uid = objectid.ObjectId(userid)
        except:
            return self.notfound()
        lives = []
        private = live_mongo.private.find({'uid':uid},skip=skip,limit=limit).sort('atime',DESCENDING)
        for k, i in enumerate(private):
            try:
                apkid = objectid.ObjectId(i['apkid'])
            except:
                continue
            else:
                apk = live_mongo.apk.find_one({'_id':apkid})
                if apk:
                    lives.append({
                        '_id':str(apk['_id']),
                        'name': apk['name'],
                        'cid': str(apk['cid']),
                        'thumbid': str(apk['thumbid'][0]),
                        })
        code = 0
        if private.count()>skip+limit:
            code=1
        self._buffer = json.dumps({'code':code, 'resp': lives})
        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)

        self.write(self._buffer)

class ThemeFavorHandler(BaseHandler):
    def get(self,userid=None):
        if not userid:
            return self.notfound()

        skip = self.get_argument("skip",default=0)
        if not skip: skip =0
        else: skip = int(skip)
        self.render("myfavortheme.html",
                context=self.context,
                userid=userid,
                skip=skip,
                )

class MoreFavorThemeHandler(BaseHandler):
    def get(self):
        limit = 18
        userid = self.get_argument("userid",default=None)
        skip = self.get_argument("skip",default=0)
        if not skip: skip=0
        else: skip=int(skip)
        if skip<1:
            limit = 9
        try:
            uid = objectid.ObjectId(userid)
        except:
            return self.notfound()
        themes = []
        private = theme_mongo.private.find({'uid':uid},skip=skip,limit=limit).sort('atime',DESCENDING)
        for k, i in enumerate(private):
            try:
                apkid = objectid.ObjectId(i['apkid'])
            except:
                continue
            else:
                apk = theme_mongo.apk.find_one({'_id':apkid})
                themes.append({
                    '_id':str(apk['_id']),
                    'name': apk['name'],
                    'cid': str(apk['cid']),
                    'thumbid': str(apk['thumbid'][0]),
                    })

        self._buffer = json.dumps({'code':0, 'resp': themes})
        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)

        self.write(self._buffer)

class PaperUploadHandler(BaseHandler):
    def get(self):
        skip = self.get_argument("offset",default=0)
        userid = self.get_argument("userid",default=None)
        #imgid = self.get_argument("imgid",default=None)

        image = mongo.image.find(
                {'uid': objectid.ObjectId(userid), 'process': True},skip=int(skip), limit=1
                ).sort('atime', DESCENDING)
        #if imgid == None:
        imgid = image[0]['_id']

        images = mongo.image.find(
                {'uid': objectid.ObjectId(userid), 'process': True}
                )
        length = images.count()
        if not skip or not userid:
            raise tornado.web.HTTPError(404)

        skip = int(skip)
        if skip<0: skip=0
        try:
            uid = objectid.ObjectId(userid)
        except:
            return self.notfound()

        try:
            imgid = objectid.ObjectId(imgid)
            image = mongo.image.find_one({'_id': imgid, 'process': True})
            if not image:
                raise
        except:
            self.flash("抱歉，您所察看的图片不存在")
            return self.notfound()

        mongo.image.update({'_id': imgid}, {'$inc': {'views': 1}})


        if skip == 0:
            front =None
        else:
            front = skip -1

        if skip == length-1:
            end = None
        else:
            end = skip+1

        tags = mongo.img2tag.find({'imgid': imgid}).sort('num', DESCENDING)
        tags =  [i for i in tags]

        referer = self.request.uri
        referer = urllib.quote(referer)

        private = False
        if self.session.login == True and mongo.private.find_one({
                'uid': self.session.uid,
                'imgid': imgid}):
                private = True
        showmsg = self.session.show_msg
        self.session.show_msg = None
        self.render("uploadpaper_detail.html",
                context=self.context,
                userid=userid,
                message=showmsg,
                referer=referer,
                image=image,
                imgid=imgid,
                tags=tags,
                front=front,
                width=self.session.width,
                height=self.session.height,
                end=end,
                private=private,
                net=self.session.net,
               )

class LiveDetailHandler(BaseHandler):
    def get(self):
        skip = self.get_argument("skip",default=None)
        userid = self.get_argument("userid",default=None)
        liveid = self.get_argument("liveid",default=None)

        if not skip or not userid:
            raise tornado.web.HTTPError(404)

        skip = int(skip)
        if skip<0: skip=0
        try:
            uid = objectid.ObjectId(userid)
        except:
            return self.notfound()

        front = -1
        end = -1
        isfav = 0

        if liveid:
            try:
                lid = objectid.ObjectId(liveid)
            except:
                return self.notfound()

            fapk = live_mongo.private.find_one({'apkid':lid,'uid':uid})
            apk = live_mongo.apk.find_one({'_id':lid})
            if fapk:
                pcount = live_mongo.private.find({'uid':uid}).count()
                if skip>=pcount and pcount>1:
                    skip=0
                    end=1
                elif skip<pcount:
                    end = skip+1
                    front = skip-1
                if end>=pcount:
                    end = -1
                isfav = 1
        else:
            privates = live_mongo.private.find({'uid':uid},skip=skip,limit=2).sort('atime',DESCENDING)
            pricount = privates.count()

            front = skip-1
            if pricount>skip:
                tmp = privates[0]
                if tmp:
                     apk = live_mongo.apk.find_one({'_id':tmp['apkid']})
            elif pricount>0:
                skip = 0
                front = skip-1
                privates = live_mongo.private.find({'uid':uid},skip=skip,limit=2).sort('atime',DESCENDING)
                tmp=privates[0]
                if tmp:
                    apk = live_mongo.private.find_one({'_id':tmp['apkid']})
            else:
                self.redirect('/livefavorlist/%s' % userid,permanent=True)

            end = skip+1
            if end>=pricount:
                end = -1
            isfav = 1


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

        referer = self.request.uri
        #referer = base64.encodestring(referer)
        referer = urllib.quote(referer)
        self.render("favorlive_detail.html",
                context=self.context,
                userid=userid,
                apk=apk,
                referer=referer,
                favstate=isfav,
               # tags=tags,
                skip=skip,
                front=front,
                end=end,
                score=score,
                amount=mcount
               )

class PaperDetailHandler(BaseHandler):
    def get(self):
        skip = self.get_argument("skip",default=None)
        userid = self.get_argument("userid",default=None)
        imgid = self.get_argument("imgid",default=None)
        if not skip or not userid:
            raise tornado.web.HTTPError(404)

        skip = int(skip)
        if skip<0: skip=0


        try:
            uid = objectid.ObjectId(userid)
        except:
            return self.notfound()

        front = -1
        end = -1
        private = False

        if imgid:
            try:
                iid = objectid.ObjectId(imgid)
            except:
                return self.notfound()

            fimg = mongo.private.find_one({'imgid':iid,'uid':uid})
            img = mongo.image.find_one({'_id':iid})
            print str(fimg)
            if fimg:
                pcount = mongo.private.find({'uid':uid}).count()
                if skip>=pcount and pcount>1:
                    skip=0
                    end=1
                elif skip<pcount:
                    end = skip+1
                    front = skip-1

                if end>=pcount:
                    end = -1
                if self.session.login == True:
                    private = True
        else:
            privates = mongo.private.find({'uid':uid},skip=skip,limit=2).sort('atime',DESCENDING)
            pricount = privates.count()

            front = skip-1
            if pricount>skip:
                tmp = privates[0]
                if tmp:
                    img = mongo.image.find_one({'_id':tmp['imgid']})
            elif pricount>0:
                skip = 0
                front = skip-1
                privates = mongo.private.find({'uid':uid},skip=skip,limit=2).sort('atime',DESCENDING)
                tmp=privates[0]
                if tmp:
                    img = mongo.image.find_one({'_id':tmp['imgid']})
            else:
                self.redirect('/paperfavorlist/%s' % userid,permanent=True)

            end = skip+1
            if end>=privates.count():
                end = -1

            if self.session.login == True:
                private = True

        mongo.image.update({'_id': img['_id']}, {'$inc': {'views': 1}})
        tags = []
        if img:
            tags = mongo.img2tag.find({'imgid':img['_id']}).sort('num', DESCENDING)
        referer = self.request.uri
        referer = urllib.quote(referer)
        showmsg = self.session.show_msg
        self.session.show_msg = None
        self.render("favorpaper_detail.html",
                context=self.context,
                message = showmsg,
                userid=userid,
                referer=referer,
                image=img,
                tags=tags,
                skip=skip,
                front=front,
                width=self.session.width,
                height=self.session.height,
                end=end,
                private=private,
                net=self.session.net,
               )




