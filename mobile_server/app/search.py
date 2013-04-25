# -*- coding: utf-8 -*-

import tornado
import urllib
from pymongo import DESCENDING, ASCENDING
from bson import objectid
import re
import json
import random
import datetime

from conf import config
from libs import BaseHandler
from db import live_mongo,mongo,theme_mongo

channel_filter = {'jifeng':
         ['火影', '海贼', '鸣人', '佐助', '路飞', '艾斯', '乔巴', '死神', '柯南'],
         'yidongmm':
         ['火影', '海贼', '鸣人', '佐助', '路飞', '艾斯', '乔巴', '死神', '柯南', '喜羊羊', 'hello kitty'],
         'tianyi':
         ['火影', '海贼', '鸣人', '佐助', '路飞', '艾斯', '乔巴', '死神', '柯南', '喜羊羊'],
       }

limit =18

def filter_deny(words):
    for i in mongo.fkilter.find():
        if i['keyword'] in words:
            return True

    return False


def __get_instant_search(words, skip, limit):
    key = ' '.join(words.split())
    key = key.replace(' ','|')

    reg = ''
    try:
        reg = re.compile(ur'%s' % key, re.IGNORECASE)
    except:
        return []

    taglist = mongo.tag.find({
        'name': reg},limit=60).sort('rank',DESCENDING)

    names = [i['name'] for i in taglist]
    
    img2tags = mongo.img2tag.find(
            {'name':{'$in':names}},
            skip=skip, limit=limit).sort("atime",DESCENDING)

    images = []
    for i in img2tags:
        img = mongo.image.find_one({'_id': i['imgid']})
        if img:
            images.append(img)

    return images, img2tags.count()


def getpaperlist(cache, queue, _search,skip, static_server, net, suid, schannel, hd):
    skip = int(skip)

    searchlist = []
    if _search:
        words = _search.strip()
    else:
        return searchlist,0

    if filter_deny(words):
        return searchlist,0

    foribtag = words.encode('utf-8')
    try:
        for i in channel_filter[schannel]:
            if i in foribtag:
                return searchlist,0
    except:
        pass

    get_in_cache = False
    try:
        imgs, length = cache.find_list(words, skip, limit-1)
        if not imgs:
            queue.add(config.Queue.cache_queue, words)
            images, length = __get_instant_search(words, skip, limit)
        else:
            get_in_cache = True
            images = [json.loads(i) for i in imgs]
    except:
        images, length = __get_instant_search(words, skip, limit)

    try:
        images[0]
    except:
        find = False
    else:
        find = True

    mongo.tag_search_log.insert({
        'tagname':words,
        'uid':suid,
        'find':find,
        'atime': datetime.datetime.now()
        })


    lfnum = len(images)%3

    isMore = 0
    if length>skip+limit:
        isMore = 1

#     if lfnum>0 and isMore==1:
#         del images[0:lfnum]

    for idx, g in enumerate(images):

        if get_in_cache:
            href = '/seapaperDetail?imgid='+str(g['_id'])+'&skip='+str(skip+idx)+"&keyword="+words+'#t1:0'+'#t0:0'
        else:
            href = '/seapaperDetail?imgid='+str(g['_id'])+"&keyword="+words+'#t1:0'+'#t0:0'

        if not hd:
            searchlist.append({
                'src':'http://'+static_server+'/download/'+str(g['thumb_fobj']),
                'num':0,
                'href': href,
                })
        elif net == 'pc':
            searchlist.append({
                'src':'http://'+static_server+'/download/'+str(g['fobjs']['640x480']),
                'num':0,
                'href': href,
                })
        else: 
            searchlist.append({
                'src':'http://'+static_server+'/download/'+str(g['fobjs']['160x120']),
                'num':0,
                'href': href,
                })
    return searchlist,isMore

def getlivelist(_search,skip,static_server,suid):
    skip = int(skip)

    searchlist = []
    if _search:
        words = _search.strip()
    else:
        words = ''

    if filter_deny(words):
        return searchlist,0

    if words != '':
        key = ' '.join(words.split())
        key = key.replace(' ','|')

        reg = ''
        try:
            reg = re.compile(ur'%s' % key, re.IGNORECASE)
        except:
            raise

        taglist = live_mongo.apk2tag.find({
            'name': reg},skip=skip,limit=limit).sort('atime',DESCENDING)

        try:
            taglist[0]
        except:
            find = False
        else:
            find = True
        live_mongo.tag_search_log.insert({
            'tagname':words,
            'uid':suid,
            'find':find,
            'atime': datetime.datetime.now()
            })
        for i in taglist:
            apk = live_mongo.apk.find_one({'_id':i['apkid']})
            if apk:
                searchlist.append({
                    'src':'http://'+static_server+'/thumbnail/'+str(apk['thumbid'][0])+'?type=1',
                    'num':1,
                    'href':'/sealiveDetail?keyword='+_search+'&skip='+str(skip)+'#t1:0'+'#t0:0'
                    })
                skip+=1
    return searchlist

def getthemelist(_search,skip,static_server):
    skip = int(skip)

    searchlist = []
    if _search:
        words = _search.strip()
    else:
        words = ''

    if filter_deny(words):
        return searchlist,0

    if words != '':
        key = ' '.join(words.split())
        key = key.replace(' ','|')

        reg = ''
        try:
            reg = re.compile(ur'%s' % key, re.IGNORECASE)
        except:
            raise

        taglist = theme_mongo.theme2tag.find({
            'name': reg},skip=skip,limit=limit).sort('num',DESCENDING)

        try:
            taglist[0]
        except:
            find = False
        else:
            find = True
        if find:
            theme_mongo.tag_search_log.insert({
                'tagname':words,
                'uid':self.session.uid,
                'find':find,
                'atime': datetime.datetime.now()
                })
        for i in taglist:
            apk = theme_mongo.apk.find_one({'_id':i['apkid']})
            searchlist.append({
                'src':'http://'+static_server+'/thumbnail/'+str(apk['thumbid'][0])+'?type=2',
                'num':2,
		'href':'/seathemeDetail?skip='+str(skip)+"&keyword="+_search+'#t1:0'+'#t0:0'
                })
            skip+=1
    return searchlist

class SearchHandler(BaseHandler):
    limit= 16
    def get(self):
        hottags = []
        newtags = []
        keyword = self.get_argument("keyword",default="")
        stype = self.get_argument("type",default="all")
        skip = self.get_argument("skip",default=0)

        newtags =list(mongo.tag_search_log.find({'find':True},limit=9).sort('atime',DESCENDING))
        newtags.extend(list(live_mongo.tag_search_log.find({'find':True},limit=9).sort('atime',DESCENDING)))
       # newtags.extend(list(theme_mongo.tag.find(limit=9).sort('atime',DESCENDING)))
        newtags.sort(reverse=True,key=lambda x:x['atime'])
        search_log = {}
        for i in newtags:
            if not search_log.has_key(i['tagname']):
                search_log[i['tagname']]=i

        hottags =list(mongo.taglog.find(limit=9).sort('count',DESCENDING))
        #hottags.extend(list(live_mongo.tag.find(limit=9).sort('rank',DESCENDING)))
        #hottags.extend(list(theme_mongo.tag.find(limit=9).sort('rank',DESCENDING)))
        #hottags.sort(reverse=True,key=lambda x:x['count'])
        if len(hottags)>9:
            hottags = hottags[:9]

        self.render("search.html",
                context=self.context,
                keyword=keyword,
                stype=stype,
                skip=skip,
                newtags=search_log,
                hottags=hottags,
               )

class SearchListHandler(BaseHandler):
    def get(self):
        ctype = self.get_argument("type",default="all")
        keyword = self.get_argument("keyword",default=None)
        if keyword:
            self.render("search_list.html",
                    context=self.context,
                    keyword=keyword,
                    stype=ctype,
                    skip=0,
                    )

class SearchPaperHandler(BaseHandler):
    def get(self):
        _search = self.get_argument('keyword',default=None)
        skip = self.get_argument('skip', default=0)
        alllist,isMore = getpaperlist(self.search_cache, self.queue, _search,skip, self.context['static_server'],
                self.session.net, self.session.uid, self.session.channel, self.session.hd)
        self._buffer = json.dumps({'code':0, 'resp':alllist,'isMore':isMore})
        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)
        self.write(self._buffer)

class SearchLiveHandler(BaseHandler):
    limit = 9
    def get(self):
        _search = self.get_argument('keyword',default=None)
        skip = self.get_argument('skip', default=0)
        alllist = getlivelist(_search,skip,self.context['static_server'],self.session.uid)
        self._buffer = json.dumps({'code':0, 'resp':alllist})
        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)
        self.write(self._buffer)

class SearchThemeHandler(BaseHandler):
    def get(self):
        _search = self.get_argument('keyword',default=None)
        skip = self.get_argument('skip', default=0)
        alllist = getthemelist(_search,skip,self.context['static_server'])
        self._buffer = json.dumps({'code':0, 'resp':alllist})
        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)
        self.write(self._buffer)

class SearchAllHandler(BaseHandler):
    def get(self):
        _search = self.get_argument('keyword',default=None)
        pskip = self.get_argument('pskip', default=0)
        lskip = self.get_argument('lskip', default=0)
     #   tskip = self.get_argument('tskip', default=0)
        alllist,isMore = getpaperlist(self.search_cache, self.queue, _search,pskip,self.context['static_server'],self.session.net,self.session.uid,self.session.channel,self.session.hd)
        alllist.extend(getlivelist(_search,lskip,self.context['static_server'],self.session.uid))
    #    alllist.extend(getthemelist(_search,tskip,self.context['static_server']))
        #random.shuffle(alllist)
        self._buffer = json.dumps({'code':0, 'resp':alllist,'isMore':isMore})
        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)
        self.write(self._buffer)

class PaperDetailHandler(BaseHandler):

    def get(self):
        imgid = self.get_argument('imgid', default=None)
        _skip = self.get_argument('skip', default=None)
        keyword = self.get_argument('keyword', default=None)
        tags = []
        cname = None

        try:
            skip = int(_skip)
        except:
            skip = 0

        previous = False
        next = False
        if _skip:
            img = self.search_cache.find_one(keyword, skip)
            if img:
                img = json.loads(img)
            else:
                raise

            if self.search_cache.find_one(keyword, skip-1):
                previous = True
            if self.search_cache.find_one(keyword, skip+1):
                next = True
        elif imgid:
            img = mongo.image.find_one({'_id': objectid.ObjectId(imgid)})
        else:
            img = None


        if img:
            tags = mongo.img2tag.find({'imgid': objectid.ObjectId(img['_id'])}).sort('num', DESCENDING)
            cate = mongo.dir.find_one({'_id': objectid.ObjectId(img['dirid'])})
            mongo.image.update({'_id': img['_id']}, {'$inc': {'views': 1}})
            if cate:
                cname = cate['rname']

        referer = self.request.uri
        referer = urllib.quote(referer)
        isfav = -1

        if self.session.uid:
            pri=mongo.private.find_one({'uid':self.session.uid,'imgid': objectid.ObjectId(img['_id'])})
            if pri:
                isfav=1
            else:
                isfav=0

        showmsg = self.session.show_msg
        self.session.show_msg = None
        self.render("seapaper_detail.html",
                context=self.context,
                referer=referer,
                message = showmsg,
                favstate=isfav,
                image=img,
                cname=cname,
                keyword=keyword,
                tags=tags,
                skip=skip,
                previous=previous,
                login=self.session.login,
                id=self.session.uid,
                next=next,
                net=self.session.net,
               )

class LiveDetailHandler(BaseHandler):
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

        taglist = live_mongo.apk2tag.find({'name': reg},skip=skip,limit=2).sort('num',DESCENDING)

        front = skip-1
        if taglist.count()>skip:
            tag=taglist[0]
        end = skip+1
        if end>=taglist.count():
            end = -1
        if tag:
            apk = live_mongo.apk.find_one({'_id':tag['apkid']})

        tags = []
        cname = None
        if apk:
            tags = live_mongo.apk2tag.find({'apkid':apk['_id']})
            cate = live_mongo.category.find_one({'_id':apk['cid']})
            if cate:
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
        self.render("sealive_detail.html",
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
                score=score,
                amount=mcount,
               )
