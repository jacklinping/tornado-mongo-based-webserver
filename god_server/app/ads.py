#-*- encoding: utf-8 -*-

import tornado
from bson import objectid
from pymongo import DESCENDING, ASCENDING

from db import mongo, live_mongo
from libs import BaseHandler

class HomeHandler(BaseHandler):

    def get(self):

        ads = mongo.adbar.find().sort('rank', ASCENDING)
        self.render("ads_list.html",
                ads = ads
                )

class HomeCreateHandler(BaseHandler):

    def get(self):
        self.render('ads_create.html')

    def post(self):
        url = self.get_argument('url', default=None)
        rank = self.get_argument('rank', default=None)

        if self.request.files:
            image = self.request.files['image'][0]
        else:
            self.message = "请上传图片"
            return self.render('ads_create.html')

        imgid = live_mongo.filefs.put(image['body']) 

        try:
            rank = int(rank)
        except:
            self.message = '排序需要一个数字'
            return self.render('ads_create.html')

        if not url or not image:
            self.message = '不能为空'
        else:
            mongo.adbar.insert({
                'url': url,
                'imgid': imgid,
                'rank': rank,
                })

        self.redirect('/ads/home')

class HomeEditHandler(BaseHandler):

    def get(self, _adsid):

        try:
            adsid = objectid.ObjectId(_adsid)
            ads = mongo.adbar.find_one({'_id': adsid})
            if not ads: raise
        except:
            self.message = "ID不存在"

        self.render('ads_edit.html',
                ads = ads
                )

    def post(self, _adsid):
        url = self.get_argument('url', default=None)
        rank = self.get_argument('rank', default=None)

        try:
            adsid = objectid.ObjectId(_adsid)
            ads = mongo.adbar.find_one({'_id': adsid})
            if not ads: raise
        except:
            self.message = "ID不存在"
            self.redirect('/ads/home')

        try:
            rank = int(rank)
        except:
            self.message = '排序需要一个数字'
            self.redirect('/ads/edit/%s' % adsid)

        if not url or not rank:
            self.message = '不能为空'
            self.redirect('/ads/edit/%s' % adsid)

        if self.request.files:
            image = self.request.files['image'][0]
            live_mongo.filefs.delete(ads['imgid'])
            imgid = live_mongo.filefs.put(image['body']) 
            ads['imgid'] = imgid

        ads['rank'] = rank
        ads['url'] = url
        mongo.adbar.save(ads)

        self.redirect('/ads/home')


class HomeDeleteHandler(BaseHandler):

    def get(self, _adsid):

        try:
            adsid = objectid.ObjectId(_adsid)
            adbar = mongo.adbar.find_one({'_id': adsid})
            if not adbar: raise
        except:
            self.message = "错误的ID"
        else:
            self.message = "删除成功"
            mongo.adbar.remove({'_id': adsid})
            live_mongo.filefs.delete(adbar['imgid'])

        self.redirect('/ads/home')

class OldHandler(BaseHandler):

    def get(self):
        acts = mongo.activity.find(limit=1).sort('atime', DESCENDING)
        try:
            activity = acts[0]
        except:
            activity = {'banner': '', 'url': ''}

        self.render('ads_old_edit.html', 
                activity=activity
                )

    def post(self):
        url = self.get_argument('url', default=None)

        acts = mongo.activity.find(limit=1).sort('atime', DESCENDING)
        try:
            activity = acts[0]
        except:
            activity = {'banner': '', 'url': ''}

        if self.request.files:
            image = self.request.files['image'][0]
        else:
            self.message = "请上传图片"
            return self.render('ads_old_edit.html',
                    activity=activity)

        if not url or not image:
            self.message = 'URL或图片不能为空'
            return self.render('ads_old_edit.html',
                    activity=activity)

        imgid = mongo.imgfs.put(image['body']) 

        import datetime
        mongo.activity.insert({
            'banner': imgid,
            'url': url,
            'atime': datetime.datetime.now()
            })

        self.redirect('/ads/old')

