#coding: utf-8
# -*- coding: utf-8 -*-

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

androidesk = conn['androidesk']
imgfs = gridfs.GridFS(conn['imgfs'])

"""user collection has 
   email:      注册邮箱 (str)
   nickname:   昵称 (str)
   passwd:     密码，明文 (str)
   avatar:     头像 (gridfs id)
   artist:     是否有创建主题权限 (bool)
   super:      是否是超级用户 (bool)
   wallpaper:  当前使用壁纸 (gridfs id)
   lastlogin:  最后一次登录 (datetime)
   IEME:       IEME (str)
   phone_number: 电话号码 (str)
   logined:    是否已登录(str)
   rank:       积分 (int)
   atime:      注册时间 (datetime)
"""
user = androidesk['user']
user.count()


"""图片主题:
   rname:      主题名 (str)
   descr:      主题描述 (str)
   hide:       主题是否被隐藏 (bool)
   uid:        创建者 (objectid)
   email:      创建者email
   nickname:   创建者昵称
   atime:      创建时间
"""
dir = androidesk['dir']
dir.count()

"""image collection has:
    fobj:       各种分辨率列表数据{'960x800': fobj, ...}
    thumb_fobj: 缩略图 (fobj)
    uid:        上传者id
    email:      上传者email
    nickname:   上传者昵称
    dirid:      所属主题id
    cid:        所属分类id
    process:    是否在处理分辨率中
    rank:       设置数
    favs:       收藏数
    views:      查看数
    atime:      上传时间
"""
image = androidesk['image']
image.count()



"""壁纸设置日志
    uid:       用户id
    imgid:     图片id
    atime:     设置时间
"""
setting_log = androidesk['log']
setting_log.count()

"""收藏日志
    uid:       用户id
    imgid:     图片id
    atime:     收藏时间
"""
private = androidesk['private']
private.count()


"""标签
    name:      标签名
    descr:     描述
    uid:       创建者id
    rank:      该标签下的图片数
    atime:     add time (datetime)
"""
tag = androidesk['tag']
tag.count()

"""图片标签对应关系
    name:     标签名
    tid:      标签id
    imgid:    图片id
    atime:    add time
"""
img2tag = androidesk['img2tag']
img2tag.count()
    

"""标签添加日志，主要用于计算单张图下标签被顶了多少次(废弃)
    uid:      用户id
    name:     标签名
    tid:      标签id
    imgid:    图片id
    atime:    add time
"""
tag_log = androidesk['tag_log']
tag_log.count()

"""顶标签日志，记录今日被顶最多的标签
   uid: 用户id
   name: 标签名
   atime: add time
   count: click count
"""
taglog = androidesk['taglog']
taglog.count()

""" 标签搜索日志
    tagname: 标签名
    uid:     用户id
    find:    搜索是否找到
    atime:   add time
"""
tag_search_log = androidesk['tag_search_log']
tag_search_log.count()

"""分类
    name:  英文名
    rname: 中文名
"""
category = androidesk['category']
category.count()

"""用户关注主题日志
    dirid: 主题id
    uid:   用户id
    atime: add time
"""
followdir = androidesk['followdir']
followdir.count()

"""
    fromuid: who leave this
    touid: who get this
    content: content
"""
reply = androidesk['reply']
reply.count()


# 以下华为这次开发暂时用不到

"""passwd_reset collection has
    email:    user email
    used:     used or not
    atime:    add time
"""
passwd_reset = androidesk['passwd_reset']
passwd_reset.count()



"""error_log has
    IMEI:
    device_model:
    network_operator:
    androidesk_version:
    android_version:
    internal_storage:
    external_storage:
"""
error_log = androidesk['error_log']
error_log.count()

"""discuss_log collection has:
    uid:       user id (str)
    imgid:     image id (mongo obj)
    atime:     datetime
"""
discuss_log = androidesk['discuss_log']
discuss_log.count()

"""feedback collection has:
    nickname: user nickname (str)
    content:  content (str)
    ip:       user ip (str)
    atime:    datetime (datetime)
"""
feedback = androidesk['feedback']
feedback.count()

"""feedback collection has:
    email: user email(str)
    content: content(str)
    atime: datetime(datetime)
"""
feed = androidesk['feed']
feed.count()

"""img_discuss collection has:
    imgid:    image id (mongo obj)
    nickname: user nickname (str)
    uid:      user id (str)
    ip:       user ip (str)
    content:  content (str)
    atime:    datetime (datetime)
"""
img_discuss = androidesk['img_discuss']
img_discuss.count()

"""device_info collection has:
    IMEI:       sim card IMEI
    deviceid:   phone device id
    devicetype: devicetype
    atime:      add time
"""
device_info = androidesk['device_info']
device_info.count()

"""device_log collection has:
    IMEI:      sim card IMEI
    deviceid:  phone device id
    atime:     addtime
"""
device_log = androidesk['device_log']
device_log.count()

"""image collection has:
    fobj:       {'resolution': fobj, ...}
    thumb_fobj: image thumb file id in GridFS
    id:         user id
    email:      user email
    nickname:   user nickname
    path:       dir path
    rank:       user rank
    pass:       0 (notpass) 1 (padding)
    reason:     if not pass, reason is here
    process:    resolution processed?
    atime:      Add time
"""
upload_image = androidesk['upload_image']
upload_image.count()


"""image hash collection has:
    hex:       sha224 hex string
    atime:     addtime
"""
image_hash = androidesk['image_hash']
image_hash.count()

"""session collection has
   uid:        user id
   email:      user email
   nickname:   user nickname
   ip:         user login ip
   session:    uuid 
   lastactive: recode user last active
   expiretime: expire datetime
   expiration: session is expired?
   atime:      add time
"""
session = androidesk['session']
session.count()

"""upload session collection has:
   fsession:   uuid
   email:      User email
   distpath:   path will upload into 
   consumerip: The ip address for the machine that will make this upload, default is the
               mechine making get_upload_url call
   expiration: The number of seconds the upload continue, Default is 20 min
   atime:      add time
"""
upload_session = androidesk['upload_session']
upload_session.count()

"""
imgid:
atime:
"""
recommend = androidesk['recommend']
recommend.count()


"""check client picture md5 or update this md5
    op:        update or delete
    md5:       client picture md5
    atime:     add time
"""
splash = androidesk['splash']
splash.count()

"""client version code
"""
version = androidesk['version']
version.count()

batchsplash = androidesk['batchsplash']
batchsplash.count()

"""top ad
image: ad image url
url: ad link url
yank: ad sort
"""
adbar = androidesk['adbar']
adbar.count()

"""
关键字过滤
keyword: 关键字
atime: 添加时间
"""
fkilter = androidesk['fkilter']

"""
老版活动banner
banner: 图片
url: 地址
atime: 添加时间
"""
activity = androidesk['activity']


"""messagedeliver collection has
   title:      message title
   content:    message content
   link:       message link
   datefrom:   vaild date like xxxx_xx_xx
   dateto:     vaild date like xxxx_xx_xx
   time:       vaild hour & minute like xxxx
   atime:      add time
"""
messagedeliver = androidesk['messagedeliver']
messagedeliver.count()
