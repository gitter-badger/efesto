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


@pytest.fixture(params=['read', 'edit', 'eliminate'])
def action(request):
    return request.param


@pytest.fixture(params=[
    {'model':Users, 'args':{'name':'u', 'email':'mail', 'password':'p', 'rank':1} },
    {'model':Types, 'args': {'name':'mytype', 'enabled':0} },
    {'model': AccessRules, 'args': {'level': 1} }
])
def item(request):
    model = request.param['model']
    item = model(**request.param['args'])
    item.save()
    def teardown():
        item.delete_instance()
    request.addfinalizer(teardown)
    return item


def test_users_can(dummy_user, action, item):
    """
    Verifies that Users.can can evaluate default permissions.
    """
    assert dummy_user.can(action, item) == False


def test_admin_can(admin_user, action, item):
    """
    Verifies that Users.can can evaluate default permissions.
    """
    assert admin_user.can(action, item) == True


def test_users_override_by_model(dummy_user, action, item):
    """
    Tests overriding an user permissions on models.
    """
    # set up
    model_name = getattr(item._meta, 'db_table')
    rule_dict = {'user': dummy_user, 'level':2, 'model':model_name}
    rule_dict[action] = 1
    rule = AccessRules(**rule_dict)
    rule.save()
    actions = ['read', 'edit', 'eliminate']
    actions.remove(action)
    # test
    assert dummy_user.can(action, item) == True
    for i in actions:
        assert dummy_user.can(i, item) == False
    # tear down
    rule.delete_instance()


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


def test_users_override_stack_by_model(dummy_user, action, item):
    """
    Tests permissions when there are more rules for the same target.
    """
    # set up
    model_name = getattr(item._meta, 'db_table')
    rule_dict = {'user': dummy_user, 'level':2, 'model':model_name}
    rule_dict[action] = 1
    rule = AccessRules(**rule_dict)
    rule.save()
    new_dict = {'user': dummy_user, 'level':3, 'model':model_name}
    new_dict[action] = 0
    new_rule = AccessRules(**new_dict)
    new_rule.save()
    # test
    assert dummy_user.can(action, item) == False
    # tear down
    new_rule.delete_instance()
    rule.delete_instance()


def test_users_override_by_item(dummy_user, action, item):
    """
    Verifies that an item rule can override a more generic model rule
    """
    # set up
    model_name = getattr(item._meta, 'db_table')
    rule_dict = {'user': dummy_user, 'level':2, 'model':model_name, 'item':item.id}
    rule_dict[action] = 1
    rule = AccessRules(**rule_dict)
    rule.save()
    second_dict = {'user': dummy_user, 'level':2, 'model':model_name}
    second_dict[action] = 0
    second_rule = AccessRules(**second_dict)
    second_rule.save()
    actions = ['read', 'edit', 'eliminate']
    actions.remove(action)
    # test
    assert dummy_user.can(action, item) == True
    for i in actions:
        assert dummy_user.can(i, item) == False
    # tear down
    rule.delete_instance()
    second_rule.delete_instance()


@pytest.mark.parametrize('args', [
    {
        'model':Users, 'args':{'name':'u', 'email':'mail', 'password':'p', 'rank':1},
        'args2':{'name':'u2', 'email':'mail', 'password':'p', 'rank':1}
    },
    {
        'model':Types, 'args': {'name':'mytype', 'enabled':0},
        'args2':{'name':'mytype2', 'enabled':0}
    },
    {
        'model':AccessRules, 'args': {'level': 1}, 'args2': {'level': 1}
    }
])
def test_users_override_check_item(dummy_user, action, args):
    """
    Verifies that permissions rules set on an item affect only the specified
    item.
    """
    model = args['model']
    model_name = getattr(model._meta, 'db_table')
    #
    item = model(**args['args'])
    item.save()
    new_item = model(**args['args2'])
    new_item.save()
    #
    rule_dict = {'user': dummy_user, 'level':2, 'model':model_name, 'item':item.id}
    rule_dict[action] = 1
    rule = AccessRules(**rule_dict)
    rule.save()
    # test
    assert dummy_user.can(action, item) == True
    assert dummy_user.can(action, new_item) == False
    # teardown
    item.delete_instance()
    new_item.delete_instance()
    rule.delete_instance()


def test_users_override_stack_by_item(dummy_user, action, item):
    """
    Tests permissions when there are more rules for the same target id.
    """
    # set up
    model_name = getattr(item._meta, 'db_table')
    rule_dict = {'user': dummy_user, 'level':2, 'model':model_name, 'item':item.id}
    rule_dict[action] = 1
    rule = AccessRules(**rule_dict)
    rule.save()
    new_dict = {'user': dummy_user, 'level':3, 'model':model_name, 'item': item.id}
    new_dict[action] = 0
    new_rule = AccessRules(**new_dict)
    new_rule.save()
    # test
    assert dummy_user.can(action, item) == False
    # tear down
    new_rule.delete_instance()
    rule.delete_instance()


def test_rank_override_by_model(dummy_user, action, item):
    """
    Tests overriding a rank permissions on models.
    """
    # set up
    model_name = getattr(item._meta, 'db_table')
    rule_dict = {'rank':dummy_user.rank, 'level':2, 'model':model_name}
    rule_dict[action] = 1
    rule = AccessRules(**rule_dict)
    rule.save()
    actions = ['read', 'edit', 'eliminate']
    actions.remove(action)
    # test
    assert dummy_user.can(action, item) == True
    for i in actions:
        assert dummy_user.can(i, item) == False
    # tear down
    rule.delete_instance()


def test_rank_override_check_model():
    raise NotImplementedError("Not implemented!")


def test_rank_override_stack_by_model():
    raise NotImplementedError("Not implemented!")


def test_rank_override_by_item():
    raise NotImplementedError("Not implemented!")


def test_rank_override_check_item():
    raise NotImplementedError("Not implemented!")


def test_rank_override_stack_by_item():
    raise NotImplementedError("Not implemented!")


def test_users_override_stack_by_item_on_model():
    raise NotImplementedError("Not implemented!")


def test_rank_override_stack_by_item_on_model():
    raise NotImplementedError("Not implemented!")


def test_users_override_rank_stack_by_model():
    raise NotImplementedError("Not implemented!")


def test_users_override_rank_stack_by_item():
    raise NotImplementedError("Not implemented!")


def test_users_override_rank_stack_by_item_on_model():
    raise NotImplementedError("Not implemented!")
