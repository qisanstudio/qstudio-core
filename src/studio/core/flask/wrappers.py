# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from flask.helpers import locked_cached_property
from flask.wrappers import Request

from studio.core.engines import shared_redis
from .users import user_meta


class StudioRequest(Request):

    @locked_cached_property
    def uid(self):
        return self.data.get('uid')

    @locked_cached_property
    def data(self):
        sid = self.cookies.get('sid')
        _data = shared_redis.get('passport-access:%s' % sid)
        try:
            _data = json.loads(_data)
        except (TypeError, ValueError):
            _data = {}
        if not isinstance(_data, dict):
            _data = {}
        return _data

    @locked_cached_property
    def current_user(self):
        return user_meta(self.uid)
