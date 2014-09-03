# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
import pytz
import re
from datetime import datetime, timedelta
from flask import current_app as app
from jinja2 import Markup
from jinja2 import evalcontextfilter
from jinja2 import escape

from studio.core.contribs import encoding


@app.template_filter()
def parseisoformat(value):
    return datetime.parseisoformat(value)


@app.template_filter()
def strfdate(value, format='%Y-%m-%d'):
    format = encoding.smart_str(format)
    return encoding.smart_unicode(value.strftime(format))

_EPOCH = datetime(1970, 1, 1, tzinfo=pytz.utc)


@app.template_filter()
def strftime(value, format='%Y-%m-%d %H:%M'):
    format = encoding.smart_str(format)
    return encoding.smart_unicode(value.strftime(format))

_EPOCH = datetime(1970, 1, 1, tzinfo=pytz.utc)


@app.template_filter()
def toepoch(dt):
    """Return POSIX timestamp as float

    Copy from Python 3.3: http://hg.python.org/cpython/rev/6671c5039e15

    """
    if not dt:
        return 0
    if dt.tzinfo is None:
        return time.mktime((dt.year, dt.month, dt.day,
                            dt.hour, dt.minute, dt.second,
                            -1, -1, -1)) + dt.microsecond / 1e6
    else:
        return (dt - _EPOCH).total_seconds()


@app.template_filter()
def time_since(dt, default='刚刚', time_format='%Y-%m-%d %H:%M'):
    """将 datetime 替换成字符串 ('3小时前', '2天前' 等等)
    的 Jinja filter copy from
    https://github.com/tonyblundell/socialdump/blob/master/socialdump.py
    sqlite 的 CURRENT_TIMESTAMP 只能使用 UTC 时间, 所以单元测试
    看到时间是8小时前的 don't panic, PostgreSQL 是有时区设定的.

    """
    # added by jade
    if not dt:
        return ''

    now = datetime.now()
    diff = now - dt
    total_seconds = diff.total_seconds()
    if total_seconds > 0:
        if total_seconds < 10800:  # 3 小时内
            periods = (
                (diff.seconds / 3600, '小时'),
                (diff.seconds / 60, '分钟'),
                (diff.seconds, '秒'),
            )
            for period, unit in periods:
                if period > 0:
                    return '%d%s前' % (period, unit)
        elif total_seconds < 86400 and dt.day == now.day:  # 严格的今天内
            return '今天' + dt.strftime('%H:%M')
        elif (total_seconds < 2 * 86400
                and dt.day == (now - timedelta(days=1)).day):  # 严格的昨天
            return '昨天' + dt.strftime('%H:%M')
        else:
            return unicode(dt.strftime(time_format))
    return default


@app.template_filter()
def extract(values, field):
    if type(values) is list:
        t = []
        for v in values:
            t.append(getattr(v, field))
        return t
    return getattr(values, field)


@app.template_filter()
def timestamp(value):
    if not isinstance(value, (int, long, float)):
        value = 0
    return datetime.fromtimestamp(value)


@app.template_filter()
def to_timestamp(dt):
    return int(time.mktime(dt.timetuple()))


@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', Markup('<br />\n'))
                          for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result
