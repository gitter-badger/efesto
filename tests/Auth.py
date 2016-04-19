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


from itsdangerous import (TimedJSONWebSignatureSerializer as TimedSerializer,
                           SignatureExpired)


from efesto.Auth import (generate_token, read_token, authenticate_by_password,
    parse_auth_header, authenticate_by_token)
from efesto.Base import config
from efesto.Models import Users, EternalTokens


@pytest.fixture
def timed_serializer():
    return TimedSerializer(config.parser.get('security', 'secret'))


def test_generate_token(timed_serializer):
    """
    Tests the generation of a token
    """
    token = generate_token(user='myuser')
    r = timed_serializer.loads(token)
    assert r == {'user':'myuser'}


def test_generate_token_expiration(timed_serializer):
    """
    Tests the generation of an expired token
    """
    token = generate_token(expiration=0, user='myuser')
    time.sleep(1)
    with pytest.raises(SignatureExpired) as e_info:
        timed_serializer.loads(token)


def test_jsonify_token(timed_serializer):
    """
    Tests whether generate_token can make a jsonificable token.
    """
    token = generate_token(user='someuser')
    jsonified_token = json.dumps({'token': token})
    assert type(jsonified_token) == str


def test_read_token(timed_serializer):
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


def test_token_authentication_failure():
    assert authenticate_by_token('notright') == None


def test_token_authentication():
    original_string = "%s:" % (generate_token(decode=True, user='user'))
    string64 = base64.b64encode( original_string.encode("latin-1") ).decode("latin-1")
    auth_string = "Basic %s" % (string64)
    result = authenticate_by_token(auth_string)
    assert result == 'user'


def test_token_authentication_eternal(dummy_admin, token):
    original_string = "%s:" % (generate_token(token=token.token))
    string64 = base64.b64encode( original_string.encode("latin-1") ).decode("latin-1")
    auth_string = "Basic %s" % (string64)
    result = authenticate_by_token(auth_string)
    assert result == dummy_admin.name
