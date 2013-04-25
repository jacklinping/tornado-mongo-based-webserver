#!/usr/bin/env python
#-*- encoding: utf-8 -*-

import os, time, datetime, random, base64
import os.path
from copy import deepcopy
import Cookie

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import hashlib
    sha1 = hashlib.sha1
except ImportError:
    import sha
    sha1 = sha.new

import utils

class Session(object):
    __slots__ = [
            "handler","store", "session_id", "_initializer", "_data", "_config", "__getitem__", "__setitem__", "__delitem__","processor"
            ]
    def __init__(self,handler,store,initializer=None):
        self.handler = handler
        self.store = store
        self._initializer = initializer
        self._data = utils.SignalDict()
        self.session_id = None
        self.__getitem__ = self._data.__getitem__
        self.__setitem__ = self._data.__setitem__
        self.__delitem__ = self._data.__delitem__


       # self._processor()

    def __contains__(self, name):
        return name in self._data

    def __getattr__(self, name):
        return getattr(self._data, name)

    def __setattr__(self, name, value):
        if name in self.__slots__:
            object.__setattr__(self, name, value)
        else:
            setattr(self._data, name, value)
            self.store[self.session_id] = dict(self._data)

    def __delattr__(self,name):
        delattr(self._data, name)

    def clean(self):
        del self.store[self.session_id]

    def processor(self,handler):
        self.handler = handler
        self._load()
        self._save()

    def _load(self):
        if not self.handler:
            return
        self.session_id = self.handler.get_secure_cookie('session_id')

        if self.session_id and not self._vaild_session_id(self.session_id):
            self.session_id = None

        if self.session_id:
            d = self.store[self.session_id]
            if d:
                self.update(d)
            else:
                self.session_id = None

        if not self.session_id:
            self.session_id = self._generate_session_id()

            if self._initializer:
                if isinstance(self._initializer, dict):
                    self.update(deepcopy(self._initializer))
                elif hasattr(self._initializer, '__call__'):
                    self._initializer()

        self.remote_ip = self.handler.request.remote_ip


    def _save(self):
        if not self.get('_killed'):
            self._setcookie(self.session_id)
            self.store[self.session_id] = dict(self._data)
        else:
            self._setcookie(self.session_id, expires=-1)

    def _cleanup(self):
        pass

    def _delSession(self):
        try:
            self.handler.clear_cookie('session_id')
            del self.store[self.session_id]
        except:
            pass
    def _vaild_session_id(self,session_id):
        rx = utils.re_compile('^[0-9a-fA-F]+$')
        if rx.match(session_id):
            return True
        
        return False

    def _generate_session_id(self):
        """Generate a random id for session"""

        while True:
            rand = os.urandom(16)
            now = time.time()
            secret_key = 'xxx'
            session_id = sha1("%s%s%s%s" % (rand, now, '1234', secret_key))
            session_id = session_id.hexdigest()
            if session_id not in self.store:
                break
        return session_id

    def _setcookie(self, session_id, expires='', **kw):
        if self.handler:
            self.handler.set_secure_cookie('session_id',session_id)



class Store:
    """Base class for session stores"""

    def __contains__(self, key):
        raise NotImplementedError

    def __getitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __cleanup(self, timeout):
        raise NotImplementedError
    
    def encode(self, session_dict):
        pickled = pickle.dumps(session_dict)
        return base64.encodestring(pickled)

    def decode(self, session_data):
        pickled = base64.decodestring(session_data)
        return pickle.loads(pickled)

