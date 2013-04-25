#!/usr/bin/python
#-*- encode: UTF-8 -*-

import os.path
import re
import tornado.web
import tornado.httpserver
import tornado.options
from tornado.options import define, options
from app import home,program,user,live,ads,feedback,messagedeliver, function

define("port", default=8888, type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers =[
                (r'/',live.HomeHandler),

                (r'/apk/upload/(.*)',program.UploadHandler),
                (r'/apk/modify/(.*)',program.ModifyHandler),
                (r'/apk/delete/(.*)',program.DeleteHandler),
                (r'/apk/show/(.*)', program.ShowHandler),

                (r'/live/home',live.HomeHandler),
                (r'/live/home/([^/]+)/(\d+)',live.HomeHandler),
                (r'/live/create',live.CreateHandler),
                (r'/live/edit/(.*)',live.EditHandler),

                (r'/ads/home', ads.HomeHandler),
                (r'/ads/home/create', ads.HomeCreateHandler),
                (r'/ads/home/edit/(.*)', ads.HomeEditHandler),
                (r'/ads/home/delete/(.*)', ads.HomeDeleteHandler),
                (r'/ads/old', ads.OldHandler),

                (r'/feedback/list', feedback.HomeHandler),
                (r'/feedback/list/(\d+)', feedback.HomeHandler),

                (r'/download/(.*)', home.DownloadHandler),

                (r'/messagedeliver/home',messagedeliver.HomeHandler),
                (r'/messagedeliver/create',messagedeliver.CreateHandler),
                (r'/messagedeliver/edit',messagedeliver.EditHandler),
                (r'/messagedeliver/delete',messagedeliver.DeleteHandler),

                (r'/function/home', function.TagHandler),
                (r'/function/tag', function.TagHandler),
                (r'/function/clean_taglog', function.CleanTaglogHandler),
                (r'/function/version', function.VersionHandler),

                (r'/login',user.LoginHandler),
                (r'/logout',user.LogoutHandler),
                ]

        settings = dict(
                template_path=os.path.join(os.path.dirname(__file__),"template"),
                static_path=os.path.join(os.path.dirname(__file__),"static"),
                xsrf_cookies=True,
                cookie_secret="aVD321fQAGaYdkLlsd334K#/adf22iNvdfdflle3fl$=",
                login_url="/login",
                autoescape=None,
                )

        tornado.web.Application.__init__(self, handlers, **settings)

#        from db import live_mongo
 #       self.db = live_mongo


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
