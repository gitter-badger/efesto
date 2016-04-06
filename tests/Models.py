# -*- coding: utf-8 -*-
"""
    The models test case.

    Tests the efesto.Models package.
"""
import sys
sys.path.insert(0, "")
import pytest
from peewee import IntegerField, CharField, DateTimeField, BooleanField, ForeignKeyField, PrimaryKeyField


from efesto.Base import db
from efesto.Models import Users, Types, Fields, AccessRules, EternalTokens, make_model
from efesto.Crypto import compare_hash


@pytest.fixture
def custom_type(request):
    new_type = Types(name='mytype', enabled=0)
    new_type.save()
    def teardown():
        new_type.delete_instance()
    request.addfinalizer(teardown)
    return new_type


@pytest.fixture
def custom_field(request, custom_type):
    new_field = Fields(name='myfield', type=custom_type.id, field_type='string')
    new_field.save()
    def teardown():
        new_field.delete_instance()
    request.addfinalizer(teardown)
    return new_field


@pytest.fixture(scope='module')
def dummy_user(request):
    db.connect()
    dummy = Users(name='dummy', email='mail', password='sample', rank=0)
    dummy.save()

    def teardown():
        dummy.delete_instance()
    request.addfinalizer(teardown)
    return dummy


@pytest.mark.parametrize('column_dict',
    [
        { 'column': 'id', 'field': PrimaryKeyField },
        { 'column': 'name', 'field': CharField, 'constraints':{'unique': True} },
        { 'column': 'email', 'field': CharField },
        { 'column': 'password', 'field': CharField},
        { 'column': 'rank', 'field': IntegerField },
        { 'column': 'last_login', 'field': DateTimeField, 'constraints':{'null': True} }
    ]
)
def test_users_model(column_dict):
    """
    Tests the Users model.
    """
    column = column_dict['column']
    field = column_dict['field']
    field_object = getattr(Users, column)
    assert isinstance(field_object, field)
    if 'constraints' in column_dict:
        constraints = column_dict['constraints']
        for constraint in constraints:
            assert getattr(field_object, constraint) == constraints[constraint]


def test_users_signal():
    """
    Verifies that the Users model hashes an user's password before saving it.
    """
    db.connect()
    dummy = Users(name='dummy2', email='mail', password='sample', rank=0)
    dummy.save()
    dummy.delete_instance()
    assert dummy.password != 'sample'
    assert compare_hash('sample', dummy.password)


def test_users_signal_on_update():
    """
    Verifies that the Users model's signal does not overwrite the password
    when is not necessary.
    """
    db.connect()
    dummy = Users(name='dummy2', email='mail', password='sample', rank=0)
    dummy.save()
    dummy.email = 'changesomeattr'
    dummy.save()
    dummy.delete_instance()
    assert compare_hash('sample', dummy.password)


@pytest.mark.parametrize('column_dict',
    [
        { 'column': 'id', 'field': PrimaryKeyField },
        { 'column': 'name', 'field': CharField, 'constraints': {'unique': True} },
        { 'column': 'enabled', 'field': BooleanField }
    ]
)
def test_types_model(column_dict):
    """
    Tests the Types model.
    """
    column = column_dict['column']
    field = column_dict['field']
    field_object = getattr(Types, column)
    assert isinstance(field_object, field)
    if 'constraints' in column_dict:
        constraints = column_dict['constraints']
        for constraint in constraints:
            assert getattr(field_object, constraint) == constraints[constraint]


@pytest.mark.parametrize('column_dict',
    [
        { 'column': 'id', 'field': PrimaryKeyField },
        { 'column': 'name', 'field': CharField },
        { 'column': 'type', 'field': ForeignKeyField },
        { 'column': 'field_type', 'field': CharField },
        { 'column': 'unique', 'field': BooleanField, 'constraints': {'null':True} },
        { 'column': 'nullable', 'field': BooleanField, 'constraints': {'null':True} },
        { 'column': 'description', 'field': CharField, 'constraints': {'null':True} },
        { 'column': 'label', 'field': CharField, 'constraints': {'null':True} }
    ]
)
def test_fields_model(column_dict):
    """
    Tests the Fields model.
    """
    column = column_dict['column']
    field = column_dict['field']
    field_object = getattr(Fields, column)
    assert isinstance(field_object, field)
    if 'constraints' in column_dict:
        constraints = column_dict['constraints']
        for constraint in constraints:
            assert getattr(field_object, constraint) == constraints[constraint]


@pytest.mark.parametrize('column_dict',
    [
        { 'column': 'id', 'field': PrimaryKeyField },
        { 'column': 'user', 'field': ForeignKeyField, 'constraints':{'null': True} },
        { 'column': 'rank', 'field': IntegerField, 'constraints':{'null': True} },
        { 'column': 'item', 'field': IntegerField, 'constraints':{'null': True} },
        { 'column': 'type', 'field': ForeignKeyField, 'constraints':{'null': True} },
        { 'column': 'level', 'field': IntegerField },
        { 'column': 'read', 'field': IntegerField, 'constraints': {'null': True} },
        { 'column': 'edit', 'field': IntegerField, 'constraints': {'null': True} },
        { 'column': 'delete', 'field': IntegerField, 'constraints':{'null': True} }
    ]
)
def test_access_rules_model(column_dict):
    """
    Tests the AccessRules model.
    """
    column = column_dict['column']
    field = column_dict['field']
    field_object = getattr(AccessRules, column)
    assert isinstance(field_object, field)
    if 'constraints' in column_dict:
        constraints = column_dict['constraints']
        for constraint in constraints:
            assert getattr(field_object, constraint) == constraints[constraint]


@pytest.mark.parametrize('column_dict', [
    { 'column': 'id', 'field': PrimaryKeyField },
    { 'column': 'name', 'field': CharField },
    { 'column': 'user', 'field': ForeignKeyField },
    { 'column': 'token', 'field': CharField }
])
def test_eternal_tokens(column_dict):
    """
    Tests the EternalTokens model
    """
    column = column_dict['column']
    field = column_dict['field']
    field_object = getattr(EternalTokens, column)
    assert isinstance(field_object, field)
    if 'constraints' in column_dict:
        constraints = column_dict['constraints']
        for constraint in constraints:
            assert getattr(field_object, constraint) == constraints[constraint]


def test_eternal_tokens_signal(dummy_user):
    """
    Tests the EternalTokens pre_save signal.
    """
    token = EternalTokens(name='randomtoken', user=dummy_user, token='')
    token.save()
    assert len(token.token) == 48
    # teardown
    token.delete_instance()


@pytest.mark.parametrize('item_dict', [
    {'model': Users, 'args': {'name':'dummy_user', 'email':'email', 'password':'passwd', 'rank':1}},
    {'model': Types, 'args': {'name':'mytype', 'enabled':0}},
    {'model': AccessRules, 'args': {'level': 1}}
])
def test_items_io(item_dict):
    """
    Verifies that is possible to create and delete items.
    """
    model = item_dict['model']
    args = item_dict['args']
    item = model(**args)
    item.save()
    assert getattr(item, 'id') != None
    item.delete_instance()


def test_fields_io():
    """
    Verfies that is possible to create and delete a Fields instance.
    """
    custom_type = Types(name='sometype', enabled=0)
    custom_type.save()
    field = Fields(name='myfield', type=custom_type.id, field_type='string')
    field.save()
    assert getattr(field, 'id') != None
    field.delete_instance()


def test_make_model_disabled(custom_type, custom_field):
    """
    Verifies that make_model raises an exception when trying to generate
    a disabled type's model.
    """
    with pytest.raises(ValueError) as e_info:
        make_model(custom_type)


def test_make_model_create_table(custom_type, custom_field):
    """
    Verifies that make_model generates the model's table.
    """
    custom_type.enabled = 1
    model = make_model(custom_type)
    assert custom_type.name in db.get_tables()


def test_make_model_columns(custom_type, custom_field):
    """
    Verifies that make_model can correctly generate a model.
    """
    custom_type.enabled = 1
    model = make_model(custom_type)
    fields_dict = {'string': CharField, 'int': IntegerField, 'bool':BooleanField }
    columns = Fields.select().where(Fields.type==custom_type.id)
    for column in columns:
        field = fields_dict[column.field_type]
        field_object = getattr(model, column.name)
        assert isinstance(field_object, field)

        if column.unique:
            assert getattr(field_object, 'unique') == True

        if column.nullable:
            assert getattr(field_object, 'nullable') == True


def test_make_model_ownership(custom_type, custom_field):
    """
    Verifies that the make_model generated model has an owner attribute.
    """
    custom_type.enabled = 1
    model = make_model(custom_type)
    assert hasattr(model, 'owner')
    assert isinstance( getattr(model, 'owner'), ForeignKeyField)
