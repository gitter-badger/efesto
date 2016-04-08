# -*- coding: utf-8 -*-
"""
    Tests permissions
"""
import sys
sys.path.insert(0, "")
import pytest


from efesto.Models import (Users, Types, Fields, AccessRules, EternalTokens,
                            make_model)
from efesto.Base import db


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


@pytest.mark.parametrize('action', ['read', 'edit', 'eliminate'])
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


@pytest.mark.parametrize('action', ['read', 'edit', 'eliminate'])
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


@pytest.mark.parametrize('action', ['read','edit', 'eliminate'])
@pytest.mark.parametrize('args', [
    {'model':Users, 'args':{'name':'u', 'email':'mail', 'password':'p', 'rank':1}},
    {'model':Types, 'args': {'name':'mytype', 'enabled':0}},
    {'model':AccessRules, 'args': {'level': 1} }
])
def test_users_override_by_model(dummy_user, action, args):
    """
    Tests overriding an user permissions on models.
    """
    # set up
    model = args['model']
    model_name = getattr(model._meta, 'db_table')
    rule_dict = {'user': dummy_user, 'level':2, 'model':model_name}
    rule_dict[action] = 1
    rule = AccessRules(**rule_dict)
    rule.save()
    actions = ['read', 'edit', 'eliminate']
    actions.remove(action)
    item = model(**args['args'])
    item.save()
    # test
    assert dummy_user.can(action, item) == True
    for i in actions:
        assert dummy_user.can(i, item) == False
    # tear down
    item.delete_instance()
    rule.delete_instance()


@pytest.mark.parametrize('action', ['read','edit', 'eliminate'])
@pytest.mark.parametrize('args', [
    {
        'model':Users, 'args':{'name':'u', 'email':'mail', 'password':'p', 'rank':1},
        'model2': Types, 'args2':{'name':'mytype', 'enabled':0}
    },
    {
        'model':Types, 'args': {'name':'mytype', 'enabled':0},
        'model2':AccessRules, 'args2':{'level': 1}
    },
    {
        'model':AccessRules, 'args': {'level': 1}, 'model2':Users,
        'args2': {'name':'u', 'email':'mail', 'password':'p', 'rank':1}
    }
])
def test_users_override_check_model(dummy_user, action, args):
    """
    Verifies that permissions rules affect only the specified model.
    """
    # set up
    model = args['model']
    model_name = getattr(model._meta, 'db_table')
    rule_dict = {'user': dummy_user, 'level':2, 'model':model_name}
    rule_dict[action] = 1
    rule = AccessRules(**rule_dict)
    rule.save()
    item = args['model2'](**args['args2'])
    item.save()
    actions = ['read', 'edit', 'eliminate']
    actions.remove(action)
    # test
    new_item = model(**args['args'])
    new_item.save()
    assert dummy_user.can(action, new_item) == True
    for i in actions:
        assert dummy_user.can(i, item) == False
    # tear down
    item.delete_instance()
    new_item.delete_instance()
    rule.delete_instance()


@pytest.mark.parametrize('action', ['read','edit', 'eliminate'])
@pytest.mark.parametrize('args', [
    {'model':Users, 'args':{'name':'u', 'email':'mail', 'password':'p', 'rank':1}},
    {'model':Types, 'args': {'name':'mytype', 'enabled':0}},
    {'model':AccessRules, 'args': {'level': 1}}
])
def test_users_override_stack_by_model(dummy_user, action, args):
    """
    Tests permissions when there are more rules for the same target.
    """
    # set up
    model = args['model']
    model_name = getattr(model._meta, 'db_table')
    rule_dict = {'user': dummy_user, 'level':2, 'model':model_name}
    rule_dict[action] = 1
    rule = AccessRules(**rule_dict)
    rule.save()
    new_dict = {'user': dummy_user, 'level':3, 'model':model_name}
    new_dict[action] = 0
    new_rule = AccessRules(**new_dict)
    new_rule.save()
    # test
    item = model(**args['args'])
    item.save()
    assert dummy_user.can(action, item) == False
    # tear down
    item.delete_instance()
    new_rule.delete_instance()
    rule.delete_instance()
