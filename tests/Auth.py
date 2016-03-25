# -*- coding: utf-8 -*-
"""
    The Auth test case.
"""
import sys
sys.path.insert(0, "")
import time
import json
import pytest


from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                           SignatureExpired)


from efesto.Config import Config
from efesto.Auth import *
from efesto.Base import db


@pytest.fixture
def config():
    return Config()


@pytest.fixture
def serializer(config):
    return Serializer(config.parser.get('main', 'secret'))


@pytest.fixture(scope='module')
def dummy_user(request):
    db.connect()
    dummy = Users(name='dummy', email='mail', password='sample', rank=0)
    dummy.save()

    def teardown():
        dummy.delete_instance()
    request.addfinalizer(teardown)
    return dummy


def test_generate_token(config, serializer):
    """
    Tests the generation of a token
    """
    token = generate_token(user='myuser')
    r = serializer.loads(token)
    assert r == {'user':'myuser'}


def test_generate_token_expiration(config, serializer):
    """
    Tests the generation of an expired token
    """
    token = generate_token(expiration=0, user='myuser')
    time.sleep(1)
    with pytest.raises(SignatureExpired) as e_info:
        serializer.loads(token)


def test_jsonify_token(config, serializer):
    """
    Tests whether generate_token can make a jsonificable token.
    """
    token = generate_token(decode=True, user='someuser')
    jsonified_token = json.dumps({'token': token})
    assert type(jsonified_token) == str


def test_read_token(config, serializer):
    """
    Tests read_token
    """
    token = generate_token(user='random')
    token_dict = read_token(token)
    assert token_dict == {'user':'random'}
