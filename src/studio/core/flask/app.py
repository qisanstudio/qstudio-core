# -*- code: utf-8 -*-
from __future__ import unicode_literals

import os
from flask import Flask
from studio.core.engines import redis
from studio.core.config import common_config_dir
from .wrappers import StudioRequest
from .session import RedisSessionInterface


__all__ = ['StudioFlask']


class StudioFlask(Flask):
    """ StudioFlask """

    request_class = StudioRequest
    session_interface = RedisSessionInterface()
    common_config_path = os.path.join(common_config_dir, 'development.pycfg')

    def __init__(self, *args, **kwargs):
        super(StudioFlask, self).__init__(*args, **kwargs)
        self.config.from_pyfile(self.common_config_path)
        app_config_path = os.path.join(self.root_path,
                                       'config',
                                       'development.pycfg')
        self.config.from_pyfile(app_config_path)
        self.secret_key = self.config.pop('SECRET_KEY', '')

        with self.app_context():
            from studio.core.engines import db
            db.init_app(self)

        if self.config.get('REDIS_URL'):
            redis.init_app(self)

        if self.config.get('ENABLE_BABEL'):
            from flask.ext.babel import Babel
            self.babel = Babel(self)

        with self.app_context():
            from . import filters  # noqa pyflakes:ignore
            from . import helpers

            self.jinja_env.globals.update(
                versioning=helpers.versioning,
            )
