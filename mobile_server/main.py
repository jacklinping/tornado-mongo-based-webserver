#!/usr/bin/python
#-*- encode: UTF-8 -*-

import os.path
import re
import tornado.web
import tornado.httpserver
import tornado.options
from tornado.options import define, options
from app import live,function,search,tag
from app import user,home,wallpaper,commend
from app import personal,status,feedback,device
# from app import theme

define("port", default=8888, type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers =[
                (r'/',home.HomeHandler),
                (r'/index',home.HomeHandler),

                (r'/paperCate',wallpaper.CategoryHandler),
                (r'/paperList',wallpaper.CategoryShowHandler),
                (r'/morepaperlist',wallpaper.MoreCateShowHandler),
                (r'/paperDetail',wallpaper.DetailHandler),
                (r'/paperdirCate',wallpaper.DirHandler),
                (r'/moredirlist',wallpaper.MoreDirHandler),
                (r'/moredirShowlist',wallpaper.MoreDirShowHandler),
                (r'/paperdirList',wallpaper.DirShowHandler),
                (r'/wallpaper',wallpaper.SettingWallpaperHandler),

                (r'/liveTips', live.TipsHandler),
                (r'/liveCate',live.CategoryHandler),
                (r'/liveList',live.ListHandler),
                (r'/liveDetail/(.*)',live.DetailHandler),
                (r'/liveMore', live.MoreListHandler),
                (r'/liveOrder', live.LiveOrderHandler),

#                 (r'/themeCate',theme.CategoryHandler),
#                 (r'/themeList',theme.ListHandler),
#                 (r'/themeDetail/(.*)',theme.DetailHandler),
#                 (r'/themeMore', theme.MoreListHandler),
#                 (r'/themeOrder',theme.OrderHandler),
#                 (r'/themeFavor', theme.FavorHandler),
#                 (r'/expthemeDetail', theme.ExplorerHandler),
#                 (r'/seathemeDetail', theme.SearchHandler),


#                (r'/explorer',explorer.ExplorerHandler), # html
#                (r'/explorerMore', explorer.MoreExplorerHandler),
#                (r'/expliveDetail/(.*)', explorer.LiveDetailHandler),
#                (r'/exppaperDetail/(.*)',explorer.PaperDetailHandler),

                (r'/explorer', commend.CommendHandler),
                (r'/newcommend', commend.NewCommendHandler),
                (r'/morepapercommend', commend.MoreNewPaperHandler),
                (r'/morelivecommend', commend.MoreNewLiveHandler),
                (r'/newpaperDetail', commend.NewPaperDetailHandler),
                (r'/newliveDetail', commend.NewLiveDetailHandler),
                (r'/hotcommend', commend.HotCommendHandler),
                (r'/morehpapercommend', commend.MoreHotPaperHandler),
                (r'/morehlivecommend', commend.MoreHotLiveHandler),

                (r'/search', search.SearchHandler), # html
                (r'/searchlist',search.SearchListHandler), # html
                (r'/searchall', search.SearchAllHandler),
                (r'/searchpaper', search.SearchPaperHandler),
                (r'/searchlive', search.SearchLiveHandler),
#                 (r'/searchtheme', search.SearchThemeHandler),
                (r'/seapaperDetail', search.PaperDetailHandler),
                (r'/sealiveDetail', search.LiveDetailHandler),


                (r'/personal', personal.PersonalHandler),
                (r'/otherprofile/(.*)',personal.OtherProfileHandler),
                (r'/myedit', personal.EditHandler),
                (r'/myfavorite/(.*)', personal.FavorHandler),
                (r'/myattention/(.*)', personal.AttentionHandler),
                (r'/moreattention', personal.MoreAttentionHandler),
                (r'/myused/(.*)', personal.UsedHandler),
                (r'/myalbum/(.*)', personal.AlbumHandler),
                (r'/morealbum', personal.MoreAlbumHandler),
                (r'/myupload/(.*)', personal.UploadHandler),
                (r'/moreupload', personal.MoreUploadHandler),
                (r'/mytag/(.*)', personal.TagHandler),
                (r'/paperfavorlist/(.*)', personal.PaperFavorHandler),
                (r'/livefavorlist/(.*)', personal.LiveFavorHandler),
                (r'/themefavorlist/(.*)', personal.ThemeFavorHandler),
                (r'/morefavorlive', personal.MoreFavorLiveHandler),
                (r'/morefavortheme', personal.MoreFavorThemeHandler),
                (r'/morefavorpaper', personal.MoreFavorPaperHandler),
                (r'/liveFavor', personal.LiveDetailHandler),
                (r'/paperFavor', personal.PaperDetailHandler),
                (r'/paperUpload', personal.PaperUploadHandler),

                (r'/add_tag', tag.TagAddHandler),
                (r'/find_tag', tag.TagFindHandler),
                (r'/morefind_tag', tag.MoreTagFindHandler),
                (r'/tagpaperDetail', tag.TagpaperDetailHandler),


                (r'/favorite/(.*)', function.LiveFavoriteHandler),
                (r'/disfavorite/(.*)', function.LiveDisFavoriteHandler),
                (r'/addfavorite/(.*)', function.AddRankHandler),
                (r'/thumbnail/(.*)', function.ThumbHandler),
                (r'/apkdata/(.*)', function.ApkDataHandler),
                (r'/versioncheck', function.CheckHandler),
                (r'/add_private', function.PaperFavoriteHandler),
                (r'/cancel_add_private', function.PaperDisFavoriteHandler),
                (r'/followPaperdir', function.PaperFollowDirHandler),
                (r'/unfollowPaperdir', function.PaperUnfollowDirHandler),
                (r'/livemark', function.LiveMarkHandler),


                (r'/login',user.LoginHandler),
                (r'/sinalogin', user.SinaOauthHandler),
                (r'/logout',user.LogoutHandler),
                (r'/user',user.UserHandler),
                (r'/checknickname',user.CheckNicknameHandler),
                (r'/signup',user.SignupHandler),
                (r'/setting',user.SettingHandler),
                (r'/findpwd',user.FindPwdHandler),
                (r'/sync_private',user.SyncPrivateHandler),
                (r'/reset_passwd',user.ResetpwdHandler),
                (r'/reset_find',user.FindResetPwdHandler),


                (r'/feedback',feedback.FeedbackHandler),
                (r'/feedbacksave',feedback.FeedbackSaveHandler),


                ('/device_start', device.StartHandler),
                ('/error_report', device.ErrorReportHandler),


                (r'/.*',status.NotfoundHandler),

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
