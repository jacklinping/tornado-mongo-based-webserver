import tornado
from bson import objectid
from pymongo import DESCENDING, ASCENDING

from db import mongo 
from libs import BaseHandler

class HomeHandler(BaseHandler):

    limit = 15

    def get(self, offset=None):

        try:
            offset = int(offset)
        except:
            offset = 0

        feedback = mongo.feed.find(skip=offset, limit=self.limit).sort(
                'datetime', DESCENDING)

        length = feedback.count()
        front, end, tail, page = self.split_page(length, offset, self.limit)

        self.render("feed_list.html",
                front=front,
                end=end,
                tail=tail,
                page=page,
                feedback=feedback
                )
