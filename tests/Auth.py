# -*- coding: utf-8 -*-
"""
    The Auth test case.
"""
import sys
sys.path.insert(0, "")
import time
import json
import base64
import pytest


from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                           SignatureExpired)


from efesto.Auth import *
from efesto.Base import db, config


@pytest.fixture
def serializer():
    return Serializer(config.parser.get('security', 'secret'))


@pytest.fixture(scope='module')
def dummy_user(request):
    db.connect()
    dummy = Users(name='dummy', email='mail', password='sample', rank=0)
    dummy.save()

    def teardown():
        dummy.delete_instance()
    request.addfinalizer(teardown)
    return dummy


@pytest.fixture
def token(request, dummy_user):
    new_token = EternalTokens(name='mytoken', user=dummy_user.id, token='token')
    new_token.save()
    def teardown():
        new_token.delete_instance()
    request.addfinalizer(teardown)
    return new_token


def test_generate_token(serializer):
    """
    Tests the generation of a token
    """
    token = generate_token(user='myuser')
    r = serializer.loads(token)
    assert r == {'user':'myuser'}


def test_generate_token_expiration(serializer):
    """
    Tests the generation of an expired token
    """
    token = generate_token(expiration=0, user='myuser')
    time.sleep(1)
    with pytest.raises(SignatureExpired) as e_info:
        serializer.loads(token)


def test_jsonify_token(serializer):
    """
    Tests whether generate_token can make a jsonificable token.
    """
    token = generate_token(decode=True, user='someuser')
    jsonified_token = json.dumps({'token': token})
    assert type(jsonified_token) == str


def test_read_token(serializer):
    """
    Tests read_token
    """
    token = generate_token(user='random')
    token_dict = read_token(token)
    assert token_dict == {'user':'random'}


def test_password_authentication_failure():
    assert authenticate_by_password('myuser', 'mypasswd') == None


def test_password_authentication_failureauthentication(dummy_user):
    assert authenticate_by_password(dummy_user.name, 'sample') == dummy_user


def test_parse_auth_header():
    original_string = "myuser:mypasswd"
    string64 = base64.b64encode( original_string.encode("latin-1") ).decode("latin-1")
    auth_string = "Basic %s" % (string64)
    result = parse_auth_header(auth_string)
    assert result == original_string
