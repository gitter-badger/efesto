# -*- coding: utf-8 -*-
"""
    The models test case.

    Tests the efesto.Models package.
"""
import sys

from efesto.Base import db
from efesto.Crypto import compare_hash
from efesto.Models import (AccessRules, EternalTokens, Fields, Types, Users,
                           make_model)
from peewee import (BooleanField, CharField, DateTimeField, ForeignKeyField,
                    IntegerField, PrimaryKeyField, TextField)
import pytest


sys.path.insert(0, '')


@pytest.fixture
def custom_type_two(request):
    new_type = Types(name='mytype2', enabled=0)
    new_type.save()

    def teardown():
        new_type.delete_instance()
    request.addfinalizer(teardown)
    return new_type


@pytest.fixture
def foreign_field(request, custom_type_two, complex_type):
    foreign_field = Fields(name='forfield', type=custom_type_two.id,
                           field_type='mytype')
    foreign_field.save()

    def teardown():
        foreign_field.delete_instance()
    request.addfinalizer(teardown)
    return foreign_field


@pytest.mark.parametrize('column_dict', [
    {'column': 'id', 'field': PrimaryKeyField},
    {'column': 'name', 'field': CharField, 'constraints': {'unique': True}},
    {'column': 'email', 'field': CharField},
    {'column': 'password', 'field': CharField},
    {'column': 'rank', 'field': IntegerField},
    {'column': 'last_login', 'field': DateTimeField,
     'constraints': {'null': True}}
])
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


@pytest.mark.parametrize('column_dict', [
    {'column': 'id', 'field': PrimaryKeyField},
    {'column': 'name', 'field': CharField, 'constraints': {'unique': True}},
    {'column': 'enabled', 'field': BooleanField}
])
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


def test_types_post_delete(dummy_user):
    """
    Tests the types post_delete signal.
    """
    new_type = Types(name='somerandtype', enabled=1)
    new_type.save()
    make_model(new_type)
    new_type.delete_instance()
    assert 'somerandtype' not in db.get_tables()


def test_types_pre_delete(dummy_user):
    new_type = Types(name='somerandtype2', enabled=1)
    new_type.save()
    model = make_model(new_type)
    new_item = model(owner=dummy_user.id)
    new_item.save()
    with pytest.raises(ValueError):
        new_type.delete_instance()
    # teardown
    new_item.delete_instance()
    new_type.delete_instance()


@pytest.mark.parametrize('column_dict', [
    {'column': 'id', 'field': PrimaryKeyField},
    {'column': 'name', 'field': CharField},
    {'column': 'type', 'field': ForeignKeyField},
    {'column': 'field_type', 'field': CharField},
    {'column': 'unique', 'field': BooleanField,
     'constraints': {'null': True}},
    {'column': 'nullable', 'field': BooleanField,
     'constraints': {'null': True}},
    {'column': 'description', 'field': CharField,
     'constraints': {'null': True}},
    {'column': 'label', 'field': CharField,
     'constraints': {'null': True}}
])
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


@pytest.mark.parametrize('column_dict', [
    {'column': 'id', 'field': PrimaryKeyField},
    {'column': 'user', 'field': ForeignKeyField,
     'constraints': {'null': True}},
    {'column': 'rank', 'field': IntegerField, 'constraints': {'null': True}},
    {'column': 'item', 'field': IntegerField, 'constraints': {'null': True}},
    {'column': 'model', 'field': CharField, 'constraints': {'null': True}},
    {'column': 'level', 'field': IntegerField},
    {'column': 'read', 'field': IntegerField, 'constraints': {'null': True}},
    {'column': 'edit', 'field': IntegerField, 'constraints': {'null': True}},
    {'column': 'eliminate', 'field': IntegerField,
     'constraints': {'null': True}}
])
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
    {'column': 'id', 'field': PrimaryKeyField},
    {'column': 'name', 'field': CharField},
    {'column': 'user', 'field': ForeignKeyField},
    {'column': 'token', 'field': CharField}
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


@pytest.mark.parametrize('item_dict', pytest.simple_items)
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
    custom_type.delete_instance()


def test_eternal_tokens_io():
    """
    Verifies that is possible to create and delete an EternalTokens instance.
    """
    user = Users(name='randuser', email='mail', password='p', rank=1)
    user.save()
    token = EternalTokens(name='mytoken', user=user.id, token='string')
    token.save()
    assert getattr(token, 'id') != None
    token.delete_instance()
    user.delete_instance()


def test_make_model_disabled(complex_type, complex_fields):
    """
    Verifies that make_model raises an exception when trying to generate
    a disabled type's model.
    """
    with pytest.raises(ValueError):
        make_model(complex_type)


def test_make_model_create_table(complex_type, complex_fields):
    """
    Verifies that make_model generates the model's table.
    """
    complex_type.enabled = 1
    make_model(complex_type)
    assert complex_type.name in db.get_tables()


def test_make_model_columns(complex_type, complex_fields):
    """
    Verifies that make_model can correctly generate a model.
    """
    complex_type.enabled = 1
    model = make_model(complex_type)
    fields_dict = {'string': TextField, 'int': IntegerField,
                   'bool': BooleanField, 'date': DateTimeField}
    columns = Fields.select().where(Fields.type == complex_type.id)
    for column in columns:
        field = fields_dict[column.field_type]
        field_object = getattr(model, column.name)
        assert isinstance(field_object, field)

        if column.unique:
            assert getattr(field_object, 'unique') == True

        if column.nullable:
            assert getattr(field_object, 'null') == True


def test_make_model_foreign_column(complex_type, custom_type_two,
                                   foreign_field):
    """
    Tests whether make_model can generate models with foreign key fields.
    """
    complex_type.enabled = 1
    complex_type.save()
    custom_type_two.enabled = 1
    model = make_model(custom_type_two)
    columns = Fields.select().where(Fields.type == custom_type_two.id,
                                    Fields.field_type == complex_type.name)
    for column in columns:
        field_object = getattr(model, column.name)
        assert isinstance(field_object, ForeignKeyField)


def test_make_model_ownership(complex_type, complex_fields):
    """
    Verifies that the make_model generated model has an owner attribute.
    """
    complex_type.enabled = 1
    model = make_model(complex_type)
    assert hasattr(model, 'owner')
    assert isinstance(getattr(model, 'owner'), ForeignKeyField)


def test_make_model_io(complex_type, complex_fields, dummy_admin):
    """
    Verifies that is possible to create and delete custom items.
    """
    complex_type.enabled = 1
    complex_type.save()
    model = make_model(complex_type)
    item_dict = {'owner': dummy_admin.id, 'intfield': 10, 'strfield': 'blah',
                 'datefield': '2016-01-01', 'ufield': 'u'}
    item = model(**item_dict)
    item.save()
    assert getattr(item, 'id') != None
    item.delete_instance()


def test_make_model_foreign_column_io(complex_type, custom_type_two,
                                      dummy_admin):
    custom_type_two.enabled = 1
    custom_type_two.save()
    complex_type.enabled = 1
    complex_type.save()
    parent_model = make_model(complex_type)
    model = make_model(custom_type_two)
    parent_item_dict = {'owner': dummy_admin.id, 'intfield': 10,
                        'strfield': 'blah', 'datefield': '2016-01-01',
                        'ufield': 'u'}
    parent_item = parent_model(**parent_item_dict)
    item = model(owner=dummy_admin.id, forfield=parent_item.id)
    item.save()
    assert getattr(item, 'id') != None
    item.delete_instance()
    parent_item.delete_instance()
