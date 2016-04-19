# -*- coding: utf-8 -*-
"""
    The Efesto authentication module.
"""
import base64
from itsdangerous import (JSONWebSignatureSerializer as Serializer,
    TimedJSONWebSignatureSerializer as TimedSerializer)


from .Models import Users, EternalTokens
from .Base import config
from .Crypto import compare_hash


def generate_token(expiration=600, **kwargs):
    s = TimedSerializer(config.parser.get('security', 'secret'), expires_in=expiration)
    return s.dumps(kwargs).decode('UTF-8')


def read_token(token):
    s = TimedSerializer(config.parser.get('security', 'secret'))
    return s.loads(token)


def authenticate_by_password(username, password):
    """
    Authenticates a user by username and password. Usually this occurs only
    when an user needs a token.
    """
    try:
        user = Users.get(Users.name == username)
        if compare_hash(password, user.password) == True:
            return user
    except:
        return None


def parse_auth_header(auth_string):
    """
    Parses a basic auth header.
    """
    return base64.b64decode(auth_string.split()[1]).decode("latin-1")


def authenticate_by_token(auth_header):
    """
    """
    try:
        auth_dict = read_token(parse_auth_header(auth_header)[:-1])
        if 'token' in auth_dict:
            return EternalTokens.get( EternalTokens.token == auth_dict['token']).user.name
        else:
            return auth_dict['user']
    except:
        return None
