# -*- coding: utf-8 -*-
"""
"""
import sys
sys.path.insert(0, "")
import falcon
import pytest


from efesto.Models import Users, EternalTokens


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
