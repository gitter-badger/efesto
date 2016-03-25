# -*- coding: utf-8 -*-
"""
    The Efesto authentication module.
"""
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


from .Models import Users
from .Config import Config


config = Config()
def generate_token(expiration=600, decode=False, **kwargs):
    s = Serializer(config.parser.get('main', 'secret'), expires_in=expiration)
    if decode == True:
        return s.dumps(kwargs).decode('UTF-8')
    return s.dumps(kwargs)


def read_token(token):
    s = Serializer(config.parser.get('main', 'secret'))
    return s.loads(token)
