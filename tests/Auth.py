# -*- coding: utf-8 -*-
"""
    The Auth test case.

    Contains tests for the Auth module or authentication-related tests.
"""
import base64
import json
import sys
import time

from efesto.Auth import (authenticate_by_token, parse_auth_header, read_token)
from efesto.Base import config
from itsdangerous import (JSONWebSignatureSerializer as Serializer,
                          SignatureExpired,
                          TimedJSONWebSignatureSerializer as TimedSerializer)
import pytest

sys.path.insert(0, '')


@pytest.fixture
def serializer():
    return Serializer(config.parser.get('security', 'secret'))


@pytest.fixture
def timed_serializer():
    return TimedSerializer(config.parser.get('security', 'secret'))


def test_generate_token(timed_serializer):
    """
    Tests the generation of a token
    """
    token = generate_token(user='myuser')
    r = timed_serializer.loads(token)
    assert r == {'user': 'myuser'}


def test_generate_token_expiration(timed_serializer):
    """
    Tests the generation of an expired token
    """
    token = generate_token(expiration=0, user='myuser')
    time.sleep(1)
    with pytest.raises(SignatureExpired):
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
    assert token_dict == {'user': 'random'}


def test_read_token_expired():
    token = generate_token(expiration=0, user='random')
    time.sleep(1)
    with pytest.raises(SignatureExpired):
        read_token(token)


def test_read_token_eternal():
    token = generate_token(expiration=-1, token='somestring')
    token_dict = read_token(token)
    assert token_dict == {'token': 'somestring'}


def test_password_authentication_failure():
    assert authenticate_by_password('myuser', 'mypasswd') == None


def test_password_authentication_disabled_user(disabled_user):
    """
    Verifies that password authentication with a disabled user fails.
    """
    assert authenticate_by_password(disabled_user.name, 'sample') is None


def test_password_authentication(dummy_user):
    """
    Verifies that successful password authentication returns the user.
    """
    assert authenticate_by_password(dummy_user.name, 'sample') == dummy_user


def test_parse_auth_header():
    original_string = 'myuser:mypasswd'
    encoded_string = original_string.encode('latin-1')
    string64 = base64.b64encode(encoded_string).decode('latin-1')
    auth_string = 'Basic %s' % (string64)
    result = parse_auth_header(auth_string)
    assert result == original_string


def test_token_authentication_failure():
    assert authenticate_by_token('notright') == None


def test_token_authentication_disabled_user(disabled_user):
    """
    Verifies that token authentication with a disabled user fails.
    """
    token = generate_token(decode=True, user=disabled_user.name)
    original_string = ':{}'.format(token)
    encoded_string = original_string.encode('latin-1')
    string64 = base64.b64encode(encoded_string).decode('latin-1')
    auth_string = 'Basic %s' % (string64)
    result = authenticate_by_token(auth_string)
    assert result is None


def test_token_authentication(dummy_user):
    token = generate_token(decode=True, user=dummy_user.name)
    original_string = 'dank:{}'.format(token)
    encoded_string = original_string.encode('latin-1')
    string64 = base64.b64encode(encoded_string).decode('latin-1')
    auth_string = 'Basic %s' % (string64)
    result = authenticate_by_token(auth_string)
    assert result == dummy_user


def test_token_auth_eternal_disabled_user(disabled_user, disabled_token):
    """
    Verifies that eternal token authentication with a disabled user fails.
    """
    token = generate_token(token=disabled_token.token)
    original_string = ':{}'.format(token)
    encoded_string = original_string.encode('latin-1')
    string64 = base64.b64encode(encoded_string).decode('latin-1')
    auth_string = 'Basic %s' % (string64)
    result = authenticate_by_token(auth_string)
    assert result is None


def test_token_authentication_eternal(dummy_admin, token):
    original_string = ':{}'.format(generate_token(token=token.token))
    encoded_string = original_string.encode('latin-1')
    string64 = base64.b64encode(encoded_string).decode('latin-1')
    auth_string = 'Basic %s' % (string64)
    result = authenticate_by_token(auth_string)
    assert result == dummy_admin
