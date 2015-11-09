#! -*- coding: utf-8 -*-

import sys
import types

from flask import helpers

from studio.core import config


class EnginesModule(types.ModuleType):
    """
        hack 模块的载入, 确保各个服务连接可以通过属性加载
    """

    @helpers.locked_cached_property
    def redis(self):
        from flask.ext.redis import Redis
        return Redis()

    @helpers.locked_cached_property
    def db(self):
        from werkzeug.local import LocalProxy
        from studio.core.sqla import SQLAlchemy

        def _find_db():
            from flask import current_app
            if current_app:
                if 'sqlalchemy' in current_app.extensions:
                    return current_app.extensions['sqlalchemy'].db
                else:
                    return SQLAlchemy(current_app)
            else:
                raise RuntimeError('working outside of application context')

        return LocalProxy(_find_db)

    @helpers.locked_cached_property
    def shared_redis(self):
        """应用间共享的redis

        """
        import redis
        url = config.SHARED_REDIS

        return redis.StrictRedis.from_url(url)

old_module = sys.modules[__name__]  # 保持引用计数
new_module = sys.modules[__name__] = EnginesModule(__name__, __doc__)
new_module.__dict__.update({
    '__file__': __file__,
    '__path__': __path__,
    '__builtins__': __builtins__,
})
