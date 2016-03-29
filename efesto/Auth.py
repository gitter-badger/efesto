# -*- coding: utf-8 -*-
"""
    The Efesto authentication module.
"""
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


from .Models import Users
from .Base import config
from .Crypto import compare_hash


def generate_token(expiration=600, decode=False, **kwargs):
    s = Serializer(config.parser.get('security', 'secret'), expires_in=expiration)
    if decode == True:
        return s.dumps(kwargs).decode('UTF-8')
    return s.dumps(kwargs)


def read_token(token):
    s = Serializer(config.parser.get('security', 'secret'))
    return s.loads(token)


def authenticate(username, password):
    try:
        user = Users.get(Users.name == username)
        return compare_hash(password, user.password)
    except:
        return False
