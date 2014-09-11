# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""获取用户元数据"""

from flask import g
from flask import current_app as app
from werkzeug import LocalProxy

from studio.core.engines import shared_redis
from studio.core.contribs.encoding import smart_unicode

#from express.models.account import AccountModel

__all__ = ['preload_user_meta', 'user_meta']


def _get_user_metadata(*uids):
    with shared_redis.pipeline() as r:
        for uid in uids:
            r.hgetall('account-metadata:%s' % uid)
        result = r.execute()

    dirty = []
    for uid, one in zip(uids, result):
        if 'uid' in one and \
           'nickname' in one and \
           'email' in one and \
           'privileges' in one:
            one['nickname'] = smart_unicode(one['nickname'])
            one['email'] = smart_unicode(one['email'])
            one['privileges'] = one['privileges'] if one['privileges'] else []
        else:
            dirty.append(uid)
    others = None
    if dirty:
        if hasattr(app, 'get_user_metadata'):
            others = app.get_user_metadata(dirty)
        else:
            others = {}#AccountModel.get_metas(uids=dirty)

    ret = {}
    for uid, one in zip(uids, result):
        if others and uid in others:
            ret[uid] = others[uid]
        elif one:
            ret[uid] = one
        else:
            ret[uid] = {
                'uid': uid,
                'nickname': 'ANONYM',
                'email': '',
                'privileges': []}

    return ret


def preload_user_meta(uids=None):
    """将指定用户预载到全局 user_meta 缓存中

    还会隐式加载 g._user_meta_uids 中的 uids

    :Parameters
        - uids 用户 uid 列表或含有 uid 的对象列表

    """
    if uids is None:
        uids = []
    if hasattr(g, '_user_meta_uids'):
        uids = uids + list(g._user_meta_uids)  # 确保创建一个新的

    uids_set = set([])

    for uid in uids:
        if uid is None or not isinstance(uid, basestring):
            continue
        uids_set.add(uid)

    if not uids_set:
        return ''

    try:
        users = _get_user_metadata(*uids_set)
    except:
        raise
    else:
        g._user_meta_uids = set([])

    try:
        g._user_meta.update(users)
    except AttributeError:
        g._user_meta = users

    return ''


def _user_meta_exists(uid):

    def proxy():
        if not hasattr(g, '_user_meta') or uid not in g._user_meta:
            # lazy loading
            preload_user_meta()

        return bool(g._user_meta[uid])  # {} or None
    return LocalProxy(proxy)


def _user_meta_value(uid, key):

    def proxy():
        if not hasattr(g, '_user_meta') or uid not in g._user_meta:
            # lazy loading
            preload_user_meta()
        try:
            return g._user_meta[uid][key]
        except (TypeError, KeyError):
            return None
    return LocalProxy(proxy)


def user_meta(uid):
    """从全局 user_meta 缓存中载入指定 uid 的字典

    :Parameters
        - uid 用户 uid 列表

    """

    if not hasattr(g, '_user_meta') or uid not in g._user_meta:
        try:
            g._user_meta_uids.add(uid)
        except AttributeError:
            g._user_meta_uids = set([uid])

    user_info = {
        'is_exists': _user_meta_exists(uid),
        'uid': _user_meta_value(uid, 'uid'),
        'nickname': _user_meta_value(uid, 'nickname'),
        'email': _user_meta_value(uid, 'email'),
        'privileges': _user_meta_value(uid, 'privileges')}

    return user_info
