# -*- coding: utf-8 -*-
"""
"""
import sys
sys.path.insert(0, "")
import falcon
import pytest
import base64


from efesto.Models import Users, EternalTokens
from efesto.Auth import generate_token


@pytest.fixture
def app():
    application = falcon.API()
    return application


@pytest.fixture(scope='session')
def dummy_admin(request):
    dummy = Users(name='dummyadmin', email='mail', password='sample', rank=10)
    dummy.save()

    def teardown():
        dummy.delete_instance()
    request.addfinalizer(teardown)
    return dummy


@pytest.fixture(scope='module')
def dummy_user(request):
    dummy = Users(name='dummyuser', email='mail', password='sample', rank=0)
    dummy.save()

    def teardown():
        dummy.delete_instance()
    request.addfinalizer(teardown)
    return dummy


@pytest.fixture
def token(request, dummy_admin):
    new_token = EternalTokens(name='mytoken', user=dummy_admin.id, token='token')
    new_token.save()
    def teardown():
        new_token.delete_instance()
    request.addfinalizer(teardown)
    return new_token


@pytest.fixture
def user_token(request, dummy_user):
    new_token = EternalTokens(name='mytoken', user=dummy_user.id, token='token')
    new_token.save()
    def teardown():
        new_token.delete_instance()
    request.addfinalizer(teardown)
    return new_token


@pytest.fixture(params=['client', 'server'])
def auth_string(request, token, dummy_admin):
    if request.param == 'client':
        token_string = "%s:" % (generate_token(decode=True, user=dummy_admin.name))
    else:
        token_string = "%s:" % (generate_token(decode=True, token=token.token))
    string64 = base64.b64encode( token_string.encode("latin-1") ).decode("latin-1")
    return "Basic %s" % (string64)
