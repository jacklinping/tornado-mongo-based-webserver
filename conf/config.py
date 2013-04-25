#coding: utf-8

class Live_wallpaper:
    savepath = "/var/livewallpaper"
    relativypath = "livewallpaper"

class Theme:
    savepath = "/var/theme"

class Path:
    import os,sys
    root_path = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
                )
            )

    tool_path = os.path.join(root_path,"tools")

    axmlprinter2 = os.path.join(tool_path, "AXMLPrinter2.jar")

class Tmp:
    androidmanifest = "/tmp/%sandroidmanifest.xml"

class Mail:
    _from = 'androidesk@androidesk.com'
    _hello_subject = '欢迎使用安卓壁纸'
    _hello_message = '您好\n感谢注册安卓壁纸(androidesk),安卓壁纸是一个为安卓手机提供壁纸下载，收藏，切换的软件，让您的手机随心而变.\n案桌壁纸http://www.androidesk.com'

    _reset_subject = '重设您在安卓壁纸的密码'
    _reset_message = '您好\n您在安卓壁纸的密码重设要求已经得到验证。请点击以下链接输入您新的密码: \n（please click on the following link to reset your password:)\nhttp://aoi.androidesk.com/reset_passwd?confirmation=%s\n如果您的email程序不支持链接点击，请将上面的地址拷贝至您的浏览器(例如IE)的地址栏进入\n感谢您对安卓壁纸的支持.'

class memcache:
    server = ['127.0.0.1:11211']
    timeout = 0

class Server:
    static_server = 'static.androidesk.com'
    apk_server = 'http://apk.androidesk.com'

class CDN:
    mhost = 'http://s.androidesk.com/aoi'

class Queue:
    host = "servern"
    port = 6379
    # queue里面的方法必须在 sbin/task_slave.py 里面实现
    mail_queue = 'send_mail'
    cache_queue = 'cache_search'
    db = 0
    queue = [mail_queue, cache_queue]


class Cache:
    master = "servero" # master只有一个，修改为master所在的内网ip, servero
    slaves = ['servero', 'serverk', 'serverl', 'serverm']  # 根据机器hostname HASH到一个slave, 可为master
    port = 6379
    db = 3 # 默认缓存DB
    searchdb = 1  # 搜索缓存DB
    imagedb = 2  # 图片缓存DB
    hot_image_cache = 'hostimage_cache' #热门图片缓存KEY

