#-*- coding: utf-8 -*-

import os
import uuid
import zipfile
import datetime
import subprocess
from xml.dom import minidom as m

from conf import config
from db import live_mongo,theme_mongo

def save_apk(fileValue):
    if not fileValue:
        return None,None,None
    filename = fileValue['filename'].replace('\\','/').split('/')[-1]
    now = datetime.datetime.now()

    savepath = os.path.join(
            config.Live_wallpaper.savepath,
            str(now.year),
            str(now.month),
            str(now.day)
            )

    if not os.path.exists(savepath):
        os.makedirs(savepath)
    savepath = os.path.join(savepath, filename)

    try:
        f = open(savepath,'w')
        f.write(fileValue['body'])
    except:
        print 'eeror'
        raise
        return None,None,None
    finally:
        f.close()

    size = os.path.getsize(savepath)
    size = size/(1024*1024.0)
    size = round(size,1)

    relatypath = os.path.join(
            config.Live_wallpaper.relativypath,
            str(now.year),
            str(now.month),
            str(now.day)
            )
    relatypath = os.path.join(relatypath,filename)

    return savepath,size,relatypath

def analyze_apk(apkpath):
    if not apkpath:
        return None,None,None

    xml = "AndroidManifest.xml"
    icon = "res/drawable/icon.png"
    icon2 = "res/drawable-nodpi/icon.png"

    iconId = None
    try:
        z = zipfile.ZipFile(apkpath)
        if xml not in z.namelist():
            raise
       # print z.namelist()
        for item in z.namelist():
            if item.count('icon.png')==1:
                iconId = live_mongo.filefs.put(z.read(item))
                break
    except:
        raise
        return None, None, None

    manifestxml = config.Tmp.androidmanifest % str(uuid.uuid4())

    with open(manifestxml,'w') as f:
        f.write(z.read(xml))

    argv = ['java','-jar', config.Path.axmlprinter2, manifestxml]
    dom = m.parseString(
            subprocess.Popen(argv, stdout=subprocess.PIPE).stdout.read()
            )
    root = dom.documentElement

    if root.hasAttribute("package"):
        package_name = root.getAttribute("package")
    else:
        package_name = None

    dd = dom.getElementsByTagName('application')[0]

    if root.hasAttribute("android:versionCode"):
        package_version = root.getAttribute("android:versionCode")
    else:
        package_version = None

    os.unlink(manifestxml)

    return package_name, package_version, iconId
