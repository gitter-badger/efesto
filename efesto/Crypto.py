# -*- coding: utf-8 -*-
"""
    Crypto
    ~~~~~~

    This module implements cryptographic functions in efesto.

    See:
    https://github.com/mitsuhiko/python-pbkdf2 (original)
    https://github.com/reedobrien/python-pbkdf2 (Python3 compatible)

    :copyright: (c) Copyright 2011 by Armin Ronacher.
    :license: BSD
"""
import hashlib
import hmac
import os
from binascii import hexlify
from itertools import starmap
from operator import xor
from struct import Struct


from .Base import config


_pack_int = Struct('>I').pack


def bytes_(s, encoding='utf8', errors='strict'):
    if isinstance(s, str):
        return s.encode(encoding, errors)
    return s


def hexlify_(s):
    return str(hexlify(s), encoding='utf8')


def range_(*args):
    return range(*args)


def pbkdf2_hex(data, salt, iterations=1000, keylen=24, hashfunc=None):
    """Like :func:`pbkdf2_bin` but returns a hex encoded string."""
    return hexlify_(pbkdf2_bin(data, salt, iterations, keylen, hashfunc))


def pbkdf2_bin(data, salt, iterations=1000, keylen=24, hashfunc=None):
    """Returns a binary digest for the PBKDF2 hash algorithm of `data`
    with the given `salt`.  It iterates `iterations` time and produces a
    key of `keylen` bytes.  By default SHA-1 is used as hash function,
    a different hashlib `hashfunc` can be provided.
    """
    hashfunc = hashfunc or hashlib.sha1
    mac = hmac.new(bytes_(data), None, hashfunc)

    def _pseudorandom(x, mac=mac):
        h = mac.copy()
        h.update(bytes_(x))
        return [x for x in h.digest()]
    buf = []
    for block in range_(1, -(-keylen // mac.digest_size) + 1):
        rv = u = _pseudorandom(bytes_(salt) + _pack_int(block))
        for i in range_(iterations - 1):
            u = _pseudorandom(bytes(u))
            rv = starmap(xor, zip(rv, u))
        buf.extend(rv)
    return bytes(buf)[:keylen]


def safe_str_cmp(a, b):
    if len(a) != len(b):
        return False
    rv = 0
    for x, y in zip(a, b):
        rv |= ord(x) ^ ord(y)
    return rv == 0


def generate_hash(string_to_hash):
    """ Generates a complete hash, that includes algorithm, iterations, salt
    and hash separated by hash_separator.

    E.g. 'PBKDF2$iterations$salt$hashed_string'
    """
    salt_length = config.parser.getint('security', 'salt_length')
    iterations = config.parser.getint('security', 'iterations')
    key_length = config.parser.getint('security', 'key_length')
    salt = hexlify_(os.urandom(salt_length))
    hashed_string = pbkdf2_hex(string_to_hash, salt, iterations=iterations,
                               keylen=key_length)
    return '$'.join(['PBKDF2-256', str(iterations), salt, hashed_string])


def compare_hash(plain_string, old_hash):
    """ Compares an hash generated with plain_string to an exisiting hash."""
    key_length = config.parser.getint('security', 'key_length')
    splitted = old_hash.split('$')
    iterations = int(splitted[1])
    salt = splitted[2]
    new_hash = pbkdf2_hex(plain_string, salt, iterations=iterations,
                          keylen=key_length)
    return safe_str_cmp(new_hash, splitted[3])
