# -*- coding: utf-8 -*-
"""
    Tests permissions
"""
import sys
sys.path.insert(0, "")
import pytest


from efesto.Models import (Users, Types, Fields, AccessRules, EternalTokens,
                            make_model)


@pytest.fixture(scope='module')
def dummy_user(request):
    dummy = Users(name='dummy', email='mail', password='sample', rank=1)
    dummy.save()

    def teardown():
        dummy.delete_instance(recursive=True, delete_nullable=True)
    request.addfinalizer(teardown)
    return dummy


@pytest.fixture(scope='module')
def admin_user(request):
    admin = Users(name='dummyadmin', email='mail', password='sample', rank=10)
    admin.save()

    def teardown():
        admin.delete_instance(recursive=True, delete_nullable=True)
    request.addfinalizer(teardown)
    return admin


@pytest.mark.parametrize('action', ['read', 'edit', 'delete'])
@pytest.mark.parametrize('args', [
    {'model':Users, 'args':{'name':'u', 'email':'mail', 'password':'p', 'rank':1} },
    {'model':Types, 'args': {'name':'mytype', 'enabled':0} },
    {'model': AccessRules, 'args': {'level': 1} }
])
def test_users_can(dummy_user, action, args):
    """
    Verifies that Users.can can evaluate default permissions.
    """
    model = args['model']
    item = model(**args['args'])
    item.save()
    assert dummy_user.can(action, item) == False
    # tear down
    item.delete_instance()


@pytest.mark.parametrize('action', ['read', 'edit', 'delete'])
@pytest.mark.parametrize('args', [
    {'model':Users, 'args':{'name':'u', 'email':'mail', 'password':'p', 'rank':1} },
    {'model':Types, 'args': {'name':'mytype', 'enabled':0} },
    {'model': AccessRules, 'args': {'level': 1} }
])
def test_admin_can(admin_user, action, args):
    """
    Verifies that Users.can can evaluate default permissions.
    """
    model = args['model']
    item = model(**args['args'])
    item.save()
    assert admin_user.can(action, item) == True
    # tear down
    item.delete_instance()
