# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
import uuid
import pkgutil
from flask import url_for, g, current_app as app


def versioning(filename, appname=None, endpoint=None):
    return url_for('static', filename=filename)
    if not endpoint:
        endpoint = 'static'
    if appname and ':' not in endpoint:
        endpoint = '%s:%s' % (appname, endpoint)
    static_hashmaps = getattr(g, 'static_hashmaps', {})

    if appname in static_hashmaps:
        hashmap = static_hashmaps[appname]

    else:
        if appname:
            loader = pkgutil.get_loader(appname)
            root_path = loader.filename if loader else None
        else:
            appname = app.name
            root_path = app.root_path

#        if app.debug and appname in config.common['DEBUG_STATIC_URL_PREFIX']:
#            # 如果开了前端调试模式, 将 URL 重写到前端的调试服务器上
#            prefix = config.common['DEBUG_STATIC_URL_PREFIX'][appname]
#            return os.path.join(prefix, filename)
#
        if root_path is None:
            # 单元测试或生产环境下, 如 app 不存在则 fallback 静默处理
            if app.debug and not app.testing:
                raise RuntimeError('Application %s is not found' % appname)
            hashmap = {}  # fallback 的 hashmap 不缓存

        else:
            fname = os.path.join(root_path, 'static', 'hashMap.json')
            if not os.path.isfile(fname):
                # 在 app 存在的情况下, hashMap.json 必须存在
                raise RuntimeError('%s is not found' % fname)
            with open(fname, 'rb') as fp:
                hashmap = json.load(fp)
            # 缓存得到的hashmap
            try:
                g.static_hashmaps[appname] = hashmap
            except AttributeError:
                g.static_hashmaps = {appname: hashmap}

    filename = filename.lstrip(os.path.sep)
    dirname, basename = os.path.split(filename)

    version = hashmap.get(filename)
    if version is None and app.debug and not app.testing:
        # 调试模式下报错, 单元测试或生产环境下静默
        raise RuntimeError('%s has no version' % filename)
    if version:
        basename = '%s.%s' % (version, basename)

    filename = os.path.join(dirname, basename)
    return url_for(endpoint, filename=filename)


def gen_uuid():
    return uuid.uuid4().hex