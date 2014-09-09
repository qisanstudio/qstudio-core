# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from wtforms.validators import Regexp, Length, ValidationError

from studio.core.contribs.encoding import smart_unicode
from iptools import IpRange


class Ukey(Regexp):
    """
    校验是否是合法的 ukey.

    """

    def __init__(self, message=None):
        super(Ukey, self).__init__(r'^[0-9a-z]{6}$', message=message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = '非法的ukey'

        super(Ukey, self).__call__(form, field)


class HTTP(Regexp):
    """
    校验是否是合法的HTTP / HTTPS URL.
    """

    def __init__(self, require_tld=True, message=None):
        tld_part = (require_tld and r'\.[a-z]{2,10}' or '')
        regex = (r'^https?://([^/:]+%s|([0-9]{1,3}\.){3}'
                 r'[0-9]{1,3})(:[0-9]+)?(\/.*)?$' % tld_part)
        super(HTTP, self).__init__(regex, re.IGNORECASE, message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = field.gettext('Invalid URL.')

        super(HTTP, self).__call__(form, field)


class Tag(Regexp):
    """
    校验是否是合法的 tag.
    """

    def __init__(self, message=None):
        super(Tag, self).__init__(r'^[0-9a-zA-Z\u00c0-\u02df\u0370-\u03ff'
                                  r'\u0400-\u052f\u3400-\u9fff!~\+ \.\-&,'
                                  r':\uff08\uff09\uff0d\u300a-\u300d·]+$',
                                  message=message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = '非法的tag'

        super(Tag, self).__call__(form, field)


class Nickname(Regexp):
    """
    校验是否是合法的昵称.

    """

    def __init__(self, message=None):
        super(Nickname, self).__init__(
            ur'[\w\u3400-\u4db5\u4e00-\u9fcb.-]{1,20}', message=message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = '昵称仅限中英文、数字、“.”、“-”及“_”'

        super(Nickname, self).__call__(form, field)


class CJKLength(Length):

    @staticmethod
    def cjk_len(text):
        text = smart_unicode(text)
        l = len(text)
        l -= len(re.findall('[\x00-\xff]', text)) / 2.0
        return l

    def __call__(self, form, field):
        l = field.data and self.cjk_len(field.data) or 0
        if l < self.min or self.max != -1 and l > self.max:
            if self.message is None:
                if self.max == -1:
                    self.message = '字段长度不得少于%(min)d个（半角字符算半个）'
                elif self.min == -1:
                    self.message = '字段长度不得多于%(max)d个（半角字符算半个）'
                else:
                    self.message = '字段长度必须在%(min)d到%(max)d之间（半角字符算半个）'

            raise ValueError(self.message % dict(min=self.min, max=self.max))


class IPAddr(object):

    """
    校验是否是合法的IP地址，接受IPv4/IPv6/CIDR的格式，不接受端口号
    """

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if self.message is None:
            self.message = "IP地址不规范"
        inputIP = field.data
        try:
            IpRange(inputIP)  # 粗筛，接受10、10/32的输入
        except TypeError:
            raise ValidationError(self.message)


class TimeString(object):

    """
    校验是否是合法的时间格式.
    接受yyyy-mm-dd,比如：2013-7-7
    可选的HH:MM:SS，比如：2013-6-31 11:11:11

    """

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if self.message is None:
            self.message = "时间格式不规范"
        inputString = field.data
        from datetime import datetime
        dtformats = (
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d %H',
            '%Y-%m-%d ',
            '%Y-%m-%d',
            '%Y-%m',
            '%Y')
        dt = None
        for dtf in dtformats:
            try:
                dt = datetime.strptime(inputString, dtf)
                break
            except ValueError:
                continue
        if not dt:
            raise ValidationError(self.message)

ukey = Ukey
nickname = Nickname
cjk_length = CJKLength
http = HTTP
timestring = TimeString
