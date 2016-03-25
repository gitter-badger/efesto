# -*- coding: utf-8 -*-
"""
    The Efesto authentication module.
"""
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


from .Models import Users
from .Config import Config


config = Config()
def generate_token(expiration=600, **kwargs):
    s = Serializer(config.parser.get('main', 'secret'), expires_in=expiration)
    return s.dumps(kwargs)


def read_token(token):
    s = Serializer(config.parser.get('main', 'secret'))
    return s.loads(token)
