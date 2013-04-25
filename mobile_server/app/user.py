#-*- coding: utf-8 -*-

import tornado
from pymongo import DESCENDING, ASCENDING
from bson import objectid
import urllib
import base64
import json
import datetime
from libs import BaseHandler
from db import mongo
from conf import config
from mixin import SinaMixin
from lib import utils

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class LoginHandler(BaseHandler):
    def get(self):
        referer = self.get_argument('next',default='/')
        message = self.get_argument('message',default=None)
        try:
            c = self.get_secure_cookie('androidesk_cookie')
            email,passwd = base64.b64decode(c).split()
            user = mongo.user.find_one({'email':email,'passwd':passwd})
            if user:
                self.session.uid = user['_id']
                self.session.avatar = user['avatar']
                self.session.nickname = user['nickname']
                self.session.email = user['email']
                self.session.super = user['super']
                self.session.artist = user['artist']
                self.session.login = True
                return self.redirect(referer)
            else:
                raise
        except:
            pass

        try:
            message = urllib.unquote(message)
        except:
            pass

        referer_quote = urllib.quote(referer)
        self.render("login.html",
                context=self.context,
                message=message,
                referer=referer,
                referer_quote=referer_quote,
                )

    def post(self):
        email = self.get_argument('email',default=None)
        passwd = self.get_argument('password',default=None)
        referer = self.get_argument('next',default='/')

        if not email or not passwd:
            return self.render("login.html",
                    context=self.context,
                    message='邮箱或密码不能为空',
                    referer=referer,
                    referer_quote=urllib.quote(referer),
                    )
        
        email = email.strip().lower()
        user = mongo.user.find_one({'email':email,'passwd':passwd})
        if not user:
            return self.render("login.html",
                    context=self.context,
                    message='邮箱或密码错误',
                    referer=referer,
                    referer_quote=urllib.quote(referer),
                    )

        mongo.user.update({'_id': user['_id']},
                {'$set': {
                    'logined': True,
                    'lastlogin': datetime.datetime.now()
                    }})

        hexstr = "%s %s" % (user['email'],user['passwd'])
        self.set_secure_cookie("androidesk_cookie",base64.b64encode(hexstr))
        self.session.uid = user['_id']
        self.session.avatar = user['avatar']
        self.session.nickname = user['nickname']
        self.session.email = user['email']
        self.session.super = user['super']
        self.session.artist = user['artist']
        self.session.login = True
        referer = referer+"#t0:0"
        self.redirect(referer)


class SinaOauthHandler(BaseHandler, SinaMixin):
    @tornado.web.asynchronous
    def get(self):
        referer = self.get_argument("referer",None)
        if self.get_argument("oauth_token", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authorize_redirect(
                self.callback_url()
                )

    def _on_auth(self, user):
        if user:
            access_token = user.get('access_token')
            if access_token:
                u = self.db.user.find_one({'openid.sina.user_id': access_token['user_id']})
                #u = None
                if not u:
                    _user = {
                            'email': None,
                            'name': user['name'],
                            'gender': None,
                            #'avatar': user['profile_image_url'],
                            'openid': {'sina': {'user_id': access_token['user_id'],'secret': access_token['secret'],'key': access_token['key']}},
                            'passwd': None,
                            'wallpaper': None,
                            'avatar': None,
                            'rand': 0,
                            'IEME': '',
                            'following': [],
                            'phone_number': '',
                            'lastlogin': datetime.datetime.now(),
                            'logined': False,
                            'super': False,
                            'artist': False,
                            'atime': datetime.datetime.now()
                        }
                    _id = self.db.user.insert(_user)
                    self.session.uid = _id
                    #self.redirect("/completeaccount?id=%s" %id)
                    self.render("complete.html",
                            _id=_id,
                            message='',
                            referer='',
                            )

                else:
                    u['name'] = user['name']
                    self.db.user.save(u)

                    self.session.uid = u['_id']
                    self.session.login = True
                    #self.redirect("/findpwd")


    def post(self):
        email = self.get_argument('email', default=None)
        password = self.get_argument('password', default=None)
        password2 = self.get_argument('password2', default=None)
        gender = self.get_argument('sex', default='0')
        referer = self.get_argument('referer',default='/')
        _id = self.get_argument('_id',default=None)
        uid = self.db.user.save({'_id':objectid.ObjectId(_id),
            'email': email.strip(),
            'passwd': password,
            'gender': gender,
            'wallpaper': None,
            'avatar': None,
            'rand': 0,
            'IEME': '',
            'following': [],
            'phone_number': '',
            'lastlogin': datetime.datetime.now(),
            'logined': True,
            'super': False,
            'artist': False,
            'atime': datetime.datetime.now()
            })

        self.redirect('/login?next=%s' % referer)
"""
class CompleteAccountHandler(BaseHandler):
    def get(self):
        _id = self.get_argument("id",None)
        if not _id:
            self.redirect("/login")

        self.render("complete.html",
              #  context=self.context,
                 message='',
                 referer='',
                )
"""
class LogoutHandler(BaseHandler):
    def get(self):
        user = self.get_current_user()
        if user:
            mongo.user.update({'_id': user},
                    {'$set':{
                        'logined': False,
                        }}
                    )
        self.session.uid = None 
        self.session.avatar = None
        self.session.nickname = None
        self.session.email = None
        self.session.super = False
        self.session.artist = False
        self.session.login = False
        self.session.clean()
        self.clear_all_cookies()
#        self.set_secure_cookie("androidesk_cookie",None)
        self.redirect("/")

class UserHandler(BaseHandler):
    def get(self):
        pass

class CheckNicknameHandler(BaseHandler):
    def get(self):
        nickname = self.get_argument('nickname',default=None)
        status = 0 #default not used
        nickname = nickname.strip()
        if not nickname: status = 0

        if mongo.user.find_one({'nickname':nickname}):
            status = 1

        self._buffer = json.dumps({'code':0, 'resp': status})
        callback = self.get_argument('jsoncallback',default=None)
        if callback:
            self._buffer = "%s(%s)" % (callback,self._buffer)

        self.write(self._buffer)

class SignupHandler(BaseHandler):
    def get(self):
        referer = self.get_argument('referer',default=None)
        if not referer: referer='/'
        self.render("signup.html",
                context=self.context,
                message=None,
                referer=referer,
                email='',
                password='',
                password2='',
                sex='0',
                nickname='',
                )

    def post(self):
        email = self.get_argument('email', default=None)
        password = self.get_argument('password', default=None)
        password2 = self.get_argument('password2', default=None)
        nickname = self.get_argument('nickname', default=None)
        gender = self.get_argument('sex', default=None)
        referer = self.get_argument('referer',default=None)

        if not gender:
            gender = self.get_argument('sex2', default='0')

        if not referer: referer='/'

        try:
            email = email.strip().lower()
            if not email: raise
        except:
            return self.render("signup.html",
                    context=self.context,
                    message='邮箱不能为空',
                    referer=refere,
                    email='',
                    sex=gender,
                    nickname=nickname,
                    password=password,
                    password2=password2,
                    )

        try:
            nickname = nickname.strip()
            if not nickname: raise
        except:
            return self.render("signup.html",
                    context=self.context,
                    message='昵称不能为空',
                    referer=refere,
                    email=email,
                    sex=gender,
                    nickname='',
                    password=password,
                    password2=password2,
                    )

        if mongo.user.find_one({'nickname':nickname}):
            return self.render("signup.html",
                    context = self.context,
                    message="该昵称已注册",
                    referer=referer,
                    email=email,
                    nickname=nickname,
                    sex=gender,
                    password=password,
                    password2=password2,
                    )

        if mongo.user.find_one({'email':email}):
            return self.render("signup.html",
                    context=self.context,
                    message='该邮箱已注册',
                    referer=referer,
                    email=email,
                    sex=gender,
                    nickname=nickname,
                    password=password,
                    password2=password2,
                    )

        uid = mongo.user.insert({
            'email': email,
            'passwd': password,
            'gender': gender,
            'nickname': nickname,
            'wallpaper': None,
            'avatar': None,
            'rank': 0,
            'IEME': '',
            'following': [],
            'phone_number': '',
            'lastlogin': datetime.datetime.now(),
            'logined': True,
            'super': False,
            'artist': False,
            'atime': datetime.datetime.now()
            })

        hexstr = "%s %s" % (email.strip(),password)
        self.set_secure_cookie("androidesk_cookie",base64.b64encode(hexstr))
        self.redirect('/login?next=%s' % referer)


class SettingHandler(BaseHandler):
    def get(self):
        pass

class FindPwdHandler(BaseHandler):
    def get(self):
        referer = self.get_argument('referer', default='/')
        self.render("findpwd.html",
                context=self.context,
                message=None,
                referer=referer,
                )

    def post(self):
        email = self.get_argument('email',default=None)
        referer = self.get_argument('referer', default='/')

        try:
            user = mongo.user.find_one({'email':email})
            if not user:
                raise
        except:
            return self.render("findpwd.html",
                    context=self.context,
                    message='该email地址还没有注册',
                    referer=referer,
                    )
        code = mongo.passwd_reset.insert({
            'used': False,
            'email': email,
            'atime': datetime.datetime.now()
            }, safe=True)

        import json
        from redis import Redis

        task = json.dumps({
            'email': email,
            'code': str(code)
            })
        self.queue.add(config.Queue.mail_queue, task)

        message = urllib.quote('找回密码已发送到您的邮箱')

        link = '/login?next=%s&message=%s' % (referer, message)
        self.redirect(link)

class ResetpwdHandler(BaseHandler):
    def get(self):
        confirmId = self.get_argument('confirmation',default=None)
        try:
            cid = objectid.ObjectId(confirmId)
            code = mongo.passwd_reset.find_one({'_id': cid})
            if code['used']:
                return self.redirect('/reset_find')
        except:
            return self.redirect('/reset_find')

        email = code['email']
        confirmation = code['_id']
        self.render("resetpwd.html",
                 context=self.context,
                 email=email,
                 confirmation=confirmation,
                 message='none',
                 )

    def post(self):
        cid = self.get_argument("confirmation",default=None)
        email = self.get_argument("email",default=None)
        newpasswd = self.get_argument("passwd",default=None)

        confirmation_id = objectid.ObjectId(cid)
        mongo.passwd_reset.update({'_id': confirmation_id}, {'$set': {'used': True}}
                                        )

        mongo.user.update(
                  {'email': email},
                  {'$set': {'passwd': newpasswd}})

        self.render("resetpwd.html",
                   context=self.context,
                   message='密码修改成功，请返回应用并登录',
                   email='',
                   confirmation='',
                   )


class FindResetPwdHandler(BaseHandler):
    def get(self):
        self.render("resetfind.html",
                context=self.context,
                message='重置码错误，请重新获取',
                )

    def post(self):
        email = self.get_argument('email',default=None)

        try:
            user = mongo.user.find_one({'email':email})
            if not user:
                raise
        except:
            return self.render("resetfind.html",
                    context=self.context,
                    message='该email地址还没有注册',
                    referer=referer,
                    )
        code = mongo.passwd_reset.insert({
            'used': False,
            'email': email,
            'atime': datetime.datetime.now()
            }, safe=True)

        import json
        from redis import Redis

        task = json.dumps({
            'email': email,
            'code': str(code)
            })
        r = Redis(host=config.Queue.host, port=config.Queue.port)
        r.lpush(config.Queue.mail_queue, task)

#         utils.sendmail(config.Mail._from,
#                 email,
#                 config.Mail._reset_subject,
#                 config.Mail._reset_message % str(code)
#                 )
        return self.render("resetfind.html",
                context=self.context,
                message='请登录您的邮件重置密码',
                )


class SyncPrivateHandler(BaseHandler):
    def get(self):
        _uid = self.get_argument('uid', default=None)
        uid = None
        try:
            uid = objectid.ObjectId(_uid)
        except:
            return self.write(json.dumps('Format error'))

        private = mongo.private.find({'uid': uid})
        privates = [str(i['imgid']) for i in private]
        return self.write(json.dumps({'privates': privates}))
