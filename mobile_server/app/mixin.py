#!/usr/bin/env python
#coding:utf-8
import tornado.auth
from tornado import escape
from urllib import quote
import urllib
from tornado import httpclient
import logging
import json

def callback_url(self):
    redirect_url = self.get_argument('path', None)
    path = self.request.path
    if redirect_url:
        if redirect_url[0] != '/':
            redirect_url = '/'+redirect_url
        path = path + '?path=%s'%quote(redirect_url)
    return path


def xxx_request(self, path, callback, access_token=None, post_args=None, **args):
    url = self._API_URL%path
    if access_token:
        all_args = {}
        all_args.update(args)
        all_args.update(post_args or {})
        consumer_token = self._oauth_consumer_token()
        method = 'POST' if post_args is not None else 'GET'
        oauth = self._oauth_request_parameters(
            url, access_token, all_args, method=method)
        args.update(oauth)
    if args: url += '?' + urllib.urlencode(args)
    callback = self.async_callback(self._on_request, callback)
    http = httpclient.AsyncHTTPClient()
    if post_args is not None:
        http.fetch(url, method='POST', body=urllib.urlencode(post_args),
                   callback=callback)
    else:
        http.fetch(url, callback=callback)

def _parse_user_response(self, callback, txt):
    if txt:
        user = json.loads(txt)
    else:
        user = None
    callback(user)

def _on_request(self, callback, response):
    if response.error:
        logging.warning('Error response %s fetching %s', response.error,
                        response.request.url)
        callback(None)
        return
    callback(response.body)


class GoogleMixin(tornado.auth.GoogleMixin):
    """
    http://openid.net.cn/specs/openid-authentication-2_0-zh_CN.html
    OpenID认证2.0——最终版

    http://code.google.com/apis/accounts/docs/OpenID.html
    Federated Login for Google Account Users

    https://www.google.com/accounts/ManageDomains
    Google openid api key

    http://code.google.com/intl/zh-CN/apis/contacts/

    http://code.google.com/intl/zh-CN/apis/contacts/docs/1.0/developers_guide_python.html
    """
    _OAUTH_VERSION = '1.0'
    callback_url = callback_url



class SinaMixin(tornado.auth.OAuthMixin):
    _OAUTH_REQUEST_TOKEN_URL = 'http://api.t.sina.com.cn/oauth/request_token'
    _OAUTH_ACCESS_TOKEN_URL = 'http://api.t.sina.com.cn/oauth/access_token'
    _OAUTH_AUTHORIZE_URL = 'http://api.t.sina.com.cn/oauth/authorize'
    _OAUTH_VERSION = '1.0a'
    _OAUTH_NO_CALLBACKS = False
    _API_URL = 'http://api.t.sina.com.cn%s.json'

    callback_url = callback_url
    _parse_user_response = _parse_user_response
    _on_request = _on_request

    def sina_request(self, path, callback, access_token=None,
                           post_args=None, **args):
        return xxx_request(
            self, path, callback, access_token, post_args, **args
        )


    def _oauth_consumer_token(self):
        return dict(
            key='4292513263',
            secret='9151dafd91735733f2dc8cbae1250e6e')

    def _oauth_get_user(self, access_token, callback):
        callback = self.async_callback(self._parse_user_response, callback)
        sina_user_id = access_token['user_id']
        self.sina_request(
            '/users/show/%s'%sina_user_id,
            access_token=access_token, callback=callback
        )


