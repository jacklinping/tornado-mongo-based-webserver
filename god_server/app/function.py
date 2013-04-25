#-*- encoding: utf-8 -*-

import tornado
from bson import objectid
from pymongo import DESCENDING, ASCENDING

from db import mongo, live_mongo
from libs import BaseHandler

DEFAULT_URL = "http://www.androidesk.com/static/androidesk.apk"

class TagHandler(BaseHandler):

    def get(self):
        self.render("function_tag.html")

class CleanTaglogHandler(BaseHandler):

    def get(self):

        mongo.taglog.remove()
        self.message = '今日热门标签已清除'
        self.render("function_tag.html")


class VersionHandler(BaseHandler):

    def get(self):
        version = mongo.version.find_one()
        if version:
            apk_url = version['apk_url']
            version_code = version['version_code']
            update_notice = version['update_notice']
        else:
            apk_url = DEFAULT_URL
            version_code = 0
            update_notice = ''

        self.render("function_version.html",
                apk_url = apk_url,
                version_code = version_code,
                update_notice = update_notice
                )

    def post(self):
        apk_url = self.get_argument('apk_url', default=DEFAULT_URL)
        _version_code = self.get_argument('version_code', default='')
        _force_update = self.get_argument('force_update', default=None)
        update_notice = self.get_argument('update_notice', default='')

        force_update = False
        if _force_update:
            force_update = True

        try:
            version_code = int(_version_code)
        except:
            version_code = 0

        ver = mongo.version.find_one()
        if not ver:
            mongo.version.insert({
                'version_code': version_code,
                'apk_url': apk_url,
                'force_update': force_update,
                'update_notice': update_notice,
                })
        else:
            mongo.version.update(
                    {'_id': ver['_id']},
                    {'$set': {
                        'version_code': version_code,
                        'apk_url': apk_url,
                        'force_update': force_update,
                        'update_notice': update_notice,
                        }})
        
        self.message = '更新版本成功'
        self.render("function_version.html",
                apk_url = apk_url,
                version_code = version_code,
                update_notice = update_notice
                )


