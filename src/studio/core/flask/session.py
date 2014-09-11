# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""Redis based session

Origin from http://flask.pocoo.org/snippets/75/

"""

import anyjson
from uuid import uuid4
from datetime import timedelta

from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin
from studio.core.engines import shared_redis


class RedisSession(CallbackDict, SessionMixin):

    def __init__(self, initial=None, sid=None, new=False):

        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class RedisSessionInterface(SessionInterface):
    serializer = anyjson
    session_class = RedisSession

    def __init__(self, redis=None, prefix='session:'):
        if redis is None:
            redis = shared_redis
        self.redis = redis
        self.prefix = prefix

    def generate_sid(self):
        return str(uuid4())

    def get_cookie_domain(self, app):
        """
            扩展原有的 cookie_domain, 增加对 X-FORWARDED-HOST 的支持
        """
#        if app.config['SESSION_COOKIE_DOMAIN_ADAPTIVE']:
#            # chop of the port which is usually not supported by browsers
#            return request.host.rsplit(':', 1)[0]
#        else:
        return super(RedisSessionInterface, self).get_cookie_domain(app)

    def get_redis_expiration_time(self, app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        return timedelta(days=1)

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self.generate_sid()
            return self.session_class(sid=sid)
        val = self.redis.get(self.prefix + sid)
        if val is not None:
            data = self.serializer.loads(val)
            return self.session_class(data, sid=sid)
        return self.session_class(sid=sid, new=True)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            self.redis.delete(self.prefix + session.sid)
            if session.modified:
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain)
            return
        redis_exp = self.get_redis_expiration_time(app, session)
        cookie_exp = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        self.redis.setex(self.prefix + session.sid,
                         int(redis_exp.total_seconds()), val)
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=cookie_exp, httponly=True,
                            domain=domain)
