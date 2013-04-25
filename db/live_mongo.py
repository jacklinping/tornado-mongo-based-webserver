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

livedesk = conn['androidesk_live_wallpaper']
filefs = gridfs.GridFS(conn['androidesk_live_wallpaper_files'])

""" 动态主题
    categroy collection has:
    name: category name
    rname: category english name
    thumbid: category thumb nail
    descr: category description
    uid: user id
    email: creator email
    nickname: creator name
    atime:
"""

category = livedesk['category']

"""动态壁纸信息
    apk collection has:
    name:
    package_name:
    package_version:
    package_size:
    package_icon:
    cid: category id
    uid: mongodb object id
    thumbid: mongodb object ids
    savepath: apk path in file system
    descr: about apk description
    author: author name
    origin: where apk from
    atime: add time
    rank: hot number
"""

apk = livedesk['apk']

"""收藏日志
    uid: user id
    apkid: apk id
    atime: favorite time
"""
private = livedesk['private']

"""标签
    name:   tag name
    descr:  tag description
    uid:    creator id
    rank:   tag  belong to apk number
    atime:  add time(datetime)
"""
tag = livedesk['tag']

"""动态壁纸与标签对应关系
    name:     tag name
    uids:     user id list
    apkid:    apk id
    num:      tag count
    atime:    add time
"""
apk2tag = livedesk['apk2tag']

""" 标签搜索日志
    tagname: 标签名
    uid:     用户id
    find:    搜索是否找到
    atime:   add time
"""
tag_search_log = livedesk['tag_search_log']
tag_search_log.count()

"""评分日志
    apkid:  apk id
    uid:    user id
    mark:   user mark
"""
mark2apk = livedesk['mark2apk']
mark2apk.count()
