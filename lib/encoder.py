# -*- coding: utf-8 -*-

from json import JSONEncoder
from bson.objectid import ObjectId
import datetime

class MongoEncoder(JSONEncoder):

    def default(self, obj, **kwargs):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return JSONEncoder.default(obj, **kwargs)

