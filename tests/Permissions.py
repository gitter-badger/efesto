# -*- coding: utf-8 -*-
"""
    Tests permissions
"""
import sys

from efesto.models import Permissions, Types, Users

import pytest


sys.path.insert(0, '')


override_check_model_params = [
    {
        'model': Users, 'args': {'name': 'u', 'email': 'mail', 'password': 'p',
                                 'rank': 1, 'enabled': 1},
        'model2': Types, 'args2': {'name': 'mytype', 'enabled': 0}
    },
    {
        'model': Types, 'args': {'name': 'mytype', 'enabled': 0},
        'model2': Permissions, 'args2': {'level': 1}
    },
    {
        'model': Permissions, 'args': {'level': 1}, 'model2': Users,
        'args2': {'name': 'u', 'email': 'mail', 'password': 'p', 'rank': 1,
                  'enabled': 1}
    }
]

override_check_item_params = [
    {
        'model': Users, 'args': {'name': 'u', 'email': 'mail', 'password': 'p',
                                 'rank': 1, 'enabled': 1},
        'args2': {'name': 'u2', 'email': 'mail', 'password': 'p', 'rank': 1,
                  'enabled': 1}
    },
    {
        'model': Types, 'args': {'name': 'mytype', 'enabled': 0},
        'args2': {'name': 'mytype2', 'enabled': 0}
    },
    {
        'model': Permissions, 'args': {'level': 1}, 'args2': {'level': 1}
    }
]


@pytest.fixture(params=['read', 'edit', 'eliminate'])
def action(request):
    return request.param


@pytest.fixture(params=pytest.simple_items)
def item(request):
    model = request.param['model']
    item = model(**request.param['args'])
    item.save()

    def teardown():
        item.delete_instance()
    request.addfinalizer(teardown)
    return item


@pytest.fixture(scope='function')
def rule(request):
    rule = Permissions(level=0)
    rule.save()

    def teardown():
        rule.delete_instance()
    request.addfinalizer(teardown)

    def update(update_dict, action, value):
        for key in update_dict:
            setattr(rule, key, update_dict[key])
        setattr(rule, action, value)
        rule.save()
    setattr(rule, 'update_from_test', update)
    return rule


def test_users_can(dummy_user, action, item):
    """
    Verifies that Users.can can evaluate default permissions.
    """
    assert dummy_user.can(action, item) == False


def test_admin_can(dummy_admin, action, item):
    """
    Verifies that Users.can can evaluate default permissions.
    """
    assert dummy_admin.can(action, item) == True


def test_users_override_by_model(dummy_user, action, item, rule):
    """
    Tests overriding an user permissions on models.
    """
    # set up
    model_name = getattr(item._meta, 'db_table')
    rule_dict = {'user': dummy_user, 'level': 2, 'model': model_name}
    rule.update_from_test(rule_dict, action, 1)
    actions = ['read', 'edit', 'eliminate']
    actions.remove(action)
    # test
    assert dummy_user.can(action, item) == True
    for i in actions:
        assert dummy_user.can(i, item) == False


@pytest.mark.parametrize('args', override_check_model_params)
def test_users_override_check_model(dummy_user, action, args, rule):
    """
    Verifies that permissions rules affect only the specified model.
    """
    # set up
    model = args['model']
    model_name = getattr(model._meta, 'db_table')
    rule_dict = {'user': dummy_user, 'level': 2, 'model': model_name}
    rule.update_from_test(rule_dict, action, 1)
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


def test_users_override_stack_by_model(dummy_user, action, item, rule):
    """
    Tests permissions when there are more rules for the same target.
    """
    # set up
    model_name = getattr(item._meta, 'db_table')
    rule_dict = {'user': dummy_user, 'level': 2, 'model': model_name}
    rule.update_from_test(rule_dict, action, 1)
    new_dict = {'user': dummy_user, 'level': 3, 'model': model_name}
    new_dict[action] = 0
    new_rule = Permissions(**new_dict)
    new_rule.save()
    # test
    assert dummy_user.can(action, item) == False
    # tear down
    new_rule.delete_instance()


def test_users_override_by_item(dummy_user, action, item, rule):
    """
    Verifies that an item rule can override a more generic model rule
    """
    # set up
    model_name = getattr(item._meta, 'db_table')
    rule_dict = {'user': dummy_user, 'level': 2, 'model': model_name,
                 'item': item.id}
    rule.update_from_test(rule_dict, action, 1)
    second_dict = {'user': dummy_user, 'level': 2, 'model': model_name}
    second_dict[action] = 0
    second_rule = Permissions(**second_dict)
    second_rule.save()
    actions = ['read', 'edit', 'eliminate']
    actions.remove(action)
    # test
    assert dummy_user.can(action, item) == True
    for i in actions:
        assert dummy_user.can(i, item) == False
        assert dummy_user.can('create', item) == False
    # tear down
    second_rule.delete_instance()


@pytest.mark.parametrize('args', override_check_item_params)
def test_users_override_check_item(dummy_user, action, args, rule):
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
    rule_dict = {'user': dummy_user, 'level': 2, 'model': model_name,
                 'item': item.id}
    rule.update_from_test(rule_dict, action, 1)
    # test
    assert dummy_user.can(action, item) == True
    assert dummy_user.can(action, new_item) == False
    # teardown
    item.delete_instance()
    new_item.delete_instance()


def test_users_override_stack_by_item(dummy_user, action, item, rule):
    """
    Tests permissions when there are more rules for the same target id.
    """
    # set up
    model_name = getattr(item._meta, 'db_table')
    rule_dict = {'user': dummy_user, 'level': 2, 'model': model_name,
                 'item': item.id}
    rule.update_from_test(rule_dict, action, 1)
    new_dict = {'user': dummy_user, 'level': 3, 'model': model_name,
                'item': item.id}
    new_dict[action] = 0
    new_rule = Permissions(**new_dict)
    new_rule.save()
    # test
    assert dummy_user.can(action, item) == False
    # tear down
    new_rule.delete_instance()


def test_rank_override_by_model(dummy_user, action, item, rule):
    """
    Tests overriding a rank permissions on models.
    """
    # set up
    model_name = getattr(item._meta, 'db_table')
    rule_dict = {'rank': dummy_user.rank, 'level': 2, 'model': model_name}
    rule.update_from_test(rule_dict, action, 1)
    actions = ['read', 'edit', 'eliminate']
    actions.remove(action)
    # test
    assert dummy_user.can(action, item) == True
    for i in actions:
        assert dummy_user.can(i, item) == False


@pytest.mark.parametrize('args', override_check_model_params)
def test_rank_override_check_model(dummy_user, action, args, rule):
    """
    Verifies that permissions rules set for a rank affect only the specified
    model.
    """
    # set up
    model = args['model']
    model_name = getattr(model._meta, 'db_table')
    rule_dict = {'rank': dummy_user.rank, 'level': 2, 'model': model_name}
    rule.update_from_test(rule_dict, action, 1)
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


def test_rank_override_stack_by_model(dummy_user, action, item, rule):
    """
    Tests permissions when there are more rules for the same rank.
    """
    # set up
    model_name = getattr(item._meta, 'db_table')
    rule_dict = {'rank': dummy_user.rank, 'level': 2, 'model': model_name}
    rule.update_from_test(rule_dict, action, 1)
    new_dict = {'rank': dummy_user.rank, 'level': 3, 'model': model_name}
    new_dict[action] = 0
    new_rule = Permissions(**new_dict)
    new_rule.save()
    # test
    assert dummy_user.can(action, item) == False
    # tear down
    new_rule.delete_instance()


def test_rank_override_by_item(dummy_user, action, item, rule):
    """
    Verifies that an item rule specified for a rank can override a more generic
    model rule for a rank.
    """
    # set up
    model_name = getattr(item._meta, 'db_table')
    rule_dict = {'rank': dummy_user.rank, 'level': 2, 'model': model_name,
                 'item': item.id}
    rule.update_from_test(rule_dict, action, 1)
    second_dict = {'rank': dummy_user.rank, 'level': 2, 'model': model_name}
    second_dict[action] = 0
    second_rule = Permissions(**second_dict)
    second_rule.save()
    actions = ['read', 'edit', 'eliminate']
    actions.remove(action)
    # test
    assert dummy_user.can(action, item) == True
    for i in actions:
        assert dummy_user.can(i, item) == False
    # tear down
    second_rule.delete_instance()


@pytest.mark.parametrize('args', override_check_item_params)
def test_rank_override_check_item(dummy_user, action, args, rule):
    """
    Verifies that permissions rules set on an item by rank affect only the
    specified item.
    """
    model = args['model']
    model_name = getattr(model._meta, 'db_table')
    #
    item = model(**args['args'])
    item.save()
    new_item = model(**args['args2'])
    new_item.save()
    #
    rule_dict = {'rank': dummy_user.rank, 'level': 2, 'model': model_name,
                 'item': item.id}
    rule.update_from_test(rule_dict, action, 1)
    # test
    assert dummy_user.can(action, item) == True
    assert dummy_user.can(action, new_item) == False
    # teardown
    item.delete_instance()
    new_item.delete_instance()


def test_rank_override_stack_by_item(dummy_user, action, item, rule):
    """
    Tests permissions when there are more rules for the same target id.
    """
    # set up
    model_name = getattr(item._meta, 'db_table')
    rule_dict = {'rank': dummy_user.rank, 'level': 2, 'model': model_name,
                 'item': item.id}
    rule.update_from_test(rule_dict, action, 1)
    new_dict = {'rank': dummy_user.rank, 'level': 3, 'model': model_name,
                'item': item.id}
    new_dict[action] = 0
    new_rule = Permissions(**new_dict)
    new_rule.save()
    # test
    assert dummy_user.can(action, item) == False
    # tear down
    new_rule.delete_instance()


def test_users_override_stack_by_item_on_model(dummy_user, action, item, rule):
    """
    Tests permissions when there is a rule on the model and an higher rule on
    the item targeting the same user.
    """
    # set up
    model_name = getattr(item._meta, 'db_table')
    rule_dict = {'user': dummy_user, 'level': 2, 'model': model_name}
    rule.update_from_test(rule_dict, action, 1)
    new_dict = {'user': dummy_user, 'level': 3, 'model': model_name,
                'item': item.id}
    new_dict[action] = 0
    new_rule = Permissions(**new_dict)
    new_rule.save()
    # test
    assert dummy_user.can(action, item) == False
    # tear down
    new_rule.delete_instance()


def test_rank_override_stack_by_item_on_model(dummy_user, action, item, rule):
    """
    Tests permissions when there is a rule on the model and an higher rule on
    the item targeting the same rank.
    """
    # set up
    model_name = getattr(item._meta, 'db_table')
    rule_dict = {'rank': dummy_user.rank, 'level': 2, 'model': model_name}
    rule.update_from_test(rule_dict, action, 1)
    new_dict = {'rank': dummy_user.rank, 'level': 3, 'model': model_name,
                'item': item.id}
    new_dict[action] = 0
    new_rule = Permissions(**new_dict)
    new_rule.save()
    # test
    assert dummy_user.can(action, item) == False
    # tear down
    new_rule.delete_instance()


def test_users_override_mixed_stack_by_item(dummy_user, action, item, rule):
    """
    Verifies that a generic rank rule is overriden by a specific user rule.
    """
    # set up
    model_name = getattr(item._meta, 'db_table')
    rule_dict = {'rank': dummy_user.rank, 'level': 2, 'model': model_name,
                 'item': item.id}
    rule.update_from_test(rule_dict, action, 1)
    new_dict = {'user': dummy_user, 'level': 2, 'model': model_name,
                'item': item.id}
    new_dict[action] = 0
    new_rule = Permissions(**new_dict)
    new_rule.save()
    # test
    assert dummy_user.can(action, item) == False
    # tear down
    new_rule.delete_instance()


def test_users_override_by_model_create(dummy_user, item, rule):
    """
    Tests overriding an user create permissions on models.
    """
    # set up
    model_name = getattr(item._meta, 'db_table')
    rule_dict = {'user': dummy_user, 'level': 2, 'model': model_name}
    rule.update_from_test(rule_dict, 'read', 5)
    actions = ['edit', 'eliminate']
    # test
    assert dummy_user.can('create', item) == True
    assert dummy_user.can('read', item) == True
    for i in actions:
        assert dummy_user.can(i, item) == False
