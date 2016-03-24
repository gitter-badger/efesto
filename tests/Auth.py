# -*- coding: utf-8 -*-
"""
    The Auth test case.
"""
import sys
sys.path.insert(0, "")
import time
import pytest


from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                           SignatureExpired)


from efesto.Config import Config
from efesto.Auth import *


@pytest.fixture
def config():
    return Config()


@pytest.fixture
def serializer(config):
    return Serializer(config.parser.get('main', 'secret'))


def test_generate_token(config, serializer):
    """
    Tests the generation of a token
    """
    token = generate_token(user='myuser')
    r = serializer.loads(token)
    assert r == {'user':'myuser'}


def test_generate_token_expiration(config, serializer):
    """
    Tests the parsing of an expired token
    """
    token = generate_token(expiration=0, user='myuser')
    time.sleep(1)
    with pytest.raises(SignatureExpired) as e_info:
        serializer.loads(token)
