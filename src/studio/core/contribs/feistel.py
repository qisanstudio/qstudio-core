# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""An implementary of feistel cipher

http://en.wikipedia.org/wiki/Feistel_cipher

"""

import struct
import hashlib


class Feistel(object):

    def __init__(self, private_key, bits=64,
                 rounds=7, digestmod=hashlib.sha1):
        if bits % 2:
            raise ValueError('bits must be even')
        self.bits = bits
        self.mask = (1L << bits) - 1
        self.half_bits = bits >> 1
        self.half_mask = (1L << self.half_bits) - 1
        self.private_key = private_key
        self.rounds = rounds
        self.digestmod = digestmod

    def __round_func(self, r, i):
        res = self.half_mask & struct.unpack(
            b'L',
            self.digestmod('%04x:%04x:%s' %
                           (r, i, self.private_key))
            .digest()[:8])[0]
        return res

    def __xxcrypt(self, d, range_func):
        d &= self.mask
        l = d >> self.half_bits
        r = d & self.half_mask
        for i in range_func():
            l, r = r, l ^ self.__round_func(r, i)
        c = l | (r << self.half_bits)
        return c

    def __encrypt_range(self):
        return xrange(self.rounds)

    def __decrypt_range(self):
        return xrange(self.rounds - 1, -1, -1)

    def encrypt(self, d):
        return self.__xxcrypt(d, self.__encrypt_range)

    def decrypt(self, d):
        return self.__xxcrypt(d, self.__decrypt_range)
