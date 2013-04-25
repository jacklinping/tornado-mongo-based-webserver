#!/usr/bin/env python
#-*- coding: utf-8 -*-

import tornado
from libs import BaseHandler
from  db import mongo
from pymongo import DESCENDING, ASCENDING
from bson import objectid

channel_filter = {'yidongmm':
         ['4e4d610cdf714d2966000003'], # 动漫
         'jifeng':
         ['4e4d610cdf714d2966000003'], # 动漫
         'tianyi':
         ['4e4d610cdf714d2966000003'], # 动漫
       }

class HomeHandler(BaseHandler):
    def get(self):
        channel = self.get_argument('channel',default=None)
        reso = self.get_argument('reso',default=None)
        version = self.get_argument('version',default=None)
        net = self.get_argument('net',default=None)
        hd = self.get_argument('hd',default=None)

        if hd:
            if hd == 'False':
                self.session.hd = False
            else:
                self.session.hd = True
        if channel:
            self.session.channel = channel

        if net:
            self.session.net = net

        if reso:
            self.session.reso = reso
            try:
                width = int(reso.split("x")[0])
                height = int(reso.split("x")[1])
                self.session.width = width
                self.session.height = height
            except:
                self.session.width = 0
                self.session.height = 0


        categorys = mongo.category.find().sort('rank', ASCENDING)
        cates = []
        for i in categorys:
            try:
                if str(i['_id']) in channel_filter[self.session.channel]:
                    continue
            except:
                pass

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

        adlist = mongo.adbar.find().sort('rank',ASCENDING)
        self.render("index.html",
                context=self.context,
                adlist=adlist,
                adlen=adlist.count(),
                cates=cates,
                )



