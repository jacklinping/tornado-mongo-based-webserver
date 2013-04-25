#-*- coding: utf-8 -*-

import gridfs
from pymongo import Connection
from pymongo.master_slave_connection import MasterSlaveConnection

import dbconf

try:
    dbconf.slave
except:
    conn = Connection(host=dbconf.master)
else:
    master_conn = Connection(host=dbconf.master)
    slave_conns = [Connection(host=i) for i in dbconf.slave]
    conn = MasterSlaveConnection(master_conn, slave_conns)

themedesk = conn['androidesk_theme_wallpaper']
filefs = gridfs.GridFS(conn['androidesk_theme_wallpaper_files'])

""" 主题分类
    categroy collection has:
    name: category name
    descr: category description
    rname: category english name
    thumbid: category thumb nail
    iconid: category icon id
    uid: user id
    email: creator email
    nickname: creator name
    atime:
"""

category = themedesk['category']

"""主题文件信息
    apk collection has:
    name:
    package_name:
    package_version:
    package_size:
    package_icon:
    cid: category id
    uid: mongodb object id
    thumbid: mongodb object id
    savepath: apk path in file system
    descr: about apk description
    author: author name
    origin: where apk from
    rank:1
    atime: add time
"""

apk = themedesk['apk']

"""收藏主题日志
    uid: user id
    apkid: theme id
    atime: favorite time
"""
private = themedesk['private']

"""标签
    name:   tag name
    descr:  tag description
    uid:    creator id
    rank:   tag  belong to theme number
    atime:  add time(datetime)
"""
tag = themedesk['tag']

"""主题与标签对应关系
    name:     tag name
    uids:     user id list
    apkid:  theme id
    num:      tag count
    atime:    add time
"""
theme2tag = themedesk['theme2tag']

