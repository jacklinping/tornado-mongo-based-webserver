# -*- coding: utf-8 -*-

from db import mongo
import tornado
import urllib
from bson import objectid
from lib.memsession import MemcacheStore
from lib.session import Session
import datetime
from libs import BaseHandler
import pymongo
from pymongo import Connection

class StartHandler(BaseHandler):
    def get(self):
        IMEI = self.get_argument("IMEI", default=None)
        deviceid = self.get_argument("deviceid", default=None)
        devicetype = self.get_argument("devicetype", default=None)
        androidesk_version = self.get_argument("androidesk_version", default=None)

        if devicetype != None:
            devicetype = urllib.unquote(devicetype)
        if androidesk_version !=None:
            androidesk_version = urllib.unquote(androidesk_version)

        if IMEI == None or deviceid == None or devicetype == None:
            return False

        if IMEI == '000000000000000' or deviceid == 'null':
            return True

        device = mongo.device_info.find_one({
            'IMEI': IMEI,
            'deviceid': deviceid
            })

        if device == None:
            mongo.device_info.insert({
                'IMEI': IMEI,
                'deviceid': deviceid,
                'devicetype': devicetype,
                'atime': datetime.datetime.now(),
                'androidesk_version': androidesk_version,
                })

        mongo.device_log.insert({
            'IMEI': IMEI,
            'deviceid': deviceid,
            'atime': datetime.datetime.now(),
            'androidesk_version': androidesk_version,
            })
        return True

class ErrorReportHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass

    def post(self):
        imei = self.get_argument("imei", default=None)
        device_model = self.get_argument("device_model", default=None)
        network_operator = self.get_argument("network_operator", default=None)
        androidesk_version = self.get_argument("androidesk_version", default=None)
        android_version = self.get_argument("android_version", default=None)
        internl_storage = self.get_argument("internl_storage", default=None)
        external_storage = self.get_argument("external_storage", default=None)
        log = self.get_argument("log", default=None)

        device = mongo.error_log.insert({
            'IMEI': imei,
            'device_model': device_model,
            'network_operator': network_operator,
            'androidesk_version': androidesk_version,
            'android_version': android_version,
            'internl_storage': internl_storage,
            'external_storage': external_storage,
            'log': log,
            })

        return True


