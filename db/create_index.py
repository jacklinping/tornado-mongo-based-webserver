#!/usr/bin/python

import mongo
from pymongo import DESCENDING

mongo.private.ensure_index([('imgid',DESCENDING), ('uid',DESCENDING)])
mongo.private.ensure_index('imgid')
mongo.private.ensure_index('uid')

mongo.device_info.ensure_index([('IMEI' ,DESCENDING), ('deviceid',DESCENDING)])
mongo.setting_log.ensure_index([('imgid',DESCENDING), ('uid',DESCENDING)])
mongo.setting_log.ensure_index('imgid', background=True)
mongo.setting_log.ensure_index([('atime', -1)])

mongo.image.ensure_index('atime')
mongo.image.ensure_index('uid')
mongo.image.ensure_index('dirid')
mongo.image.ensure_index('cid')
mongo.image.ensure_index('process')
mongo.image.ensure_index([('process', 1), ('atime', -1)])
mongo.image.ensure_index([('process', 1), ('dirid', 1)])
mongo.image.ensure_index([('process', 1), ('cid', 1)])
mongo.image.ensure_index([('process', 1), ('rank', -1)])
mongo.image.ensure_index([('process', 1), ('dirid', 1), ('atime', -1)])
mongo.image.ensure_index([('process', 1), ('cid', 1), ('atime', -1)])

mongo.tag.ensure_index('uid')
mongo.tag.ensure_index('name')
mongo.tag.ensure_index('rank')

mongo.tag_log.ensure_index('uid')
mongo.tag_log.ensure_index('imgid')
mongo.tag_log.ensure_index('atime')
mongo.img2tag.ensure_index('tid')
mongo.img2tag.ensure_index('imgid')
mongo.img2tag.ensure_index([('imgid', 1), ('name', 1)])

mongo.img2tag.ensure_index('name')
mongo.img2tag.ensure_index([('name', 1), ('atime', -1)])
mongo.img2tag.ensure_index([('name', 1), ('imgid', 1)])
mongo.img2tag.ensure_index([('name', 1), ('imgid', 1), ('uids', 1)])

mongo.user.ensure_index('email')
mongo.user.ensure_index('nickname')
mongo.user.ensure_index('rank')
mongo.user.ensure_index('atime')
mongo.user.ensure_index('wallpaper')
mongo.user.ensure_index('wallpaper_setime')

mongo.tag_search_log.ensure_index([('atime', -1)])
mongo.tag_search_log.ensure_index('tagname')

mongo.followdir.ensure_index('dirid')

import live_mongo
live_mongo.tag_search_log.ensure_index([('atime', -1)], unique=False)
live_mongo.tag_search_log.ensure_index([('find', 1)], unique=False)
live_mongo.tag_search_log.ensure_index([('find', 1), ('atime', -1)], unique=False)

live_mongo.private.ensure_index([('apkid',DESCENDING), ('uid',DESCENDING)])
live_mongo.private.ensure_index('apkid')
live_mongo.private.ensure_index('uid')
