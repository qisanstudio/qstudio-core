# -*- coding: utf-8 -*-
"""62进制和int互相转换模块"""

__all__ = ['base62_encode', 'base62_decode']

digits = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
digits_map = {s: i for i, s in enumerate(digits)}


def base62_encode(number):
    assert number >= 0, 'positive integer required'
    if number == 0:
        return '0'
    b62 = []
    while number != 0:
        number, i = divmod(number, 62)
        b62.append(digits[i])
    return ''.join(reversed(b62))


def base62_decode(text):
    textlen = len(text)
    num = 0

    for idx, char in enumerate(text):
        power = (textlen - (idx + 1))
        num += digits_map[char] * (62 ** power)

    return num
