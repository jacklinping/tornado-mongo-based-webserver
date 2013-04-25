#-*- coding: utf-8 -*-

import tornado
import json
import urllib
import datetime
import base64
from libs import BaseHandler

class NotfoundHandler(BaseHandler):
    def get(self):
        self.render("notfound.html",
                )

