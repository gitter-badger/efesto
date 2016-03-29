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
from efesto.Models import Users, Types, Fields, AccessRules
from efesto.Crypto import compare_hash


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


@pytest.mark.parametrize('column_dict',
    [
        { 'column': 'id', 'field': PrimaryKeyField },
        { 'column': 'name', 'field': CharField },
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


@pytest.mark.parametrize('column_dict',
    [
        { 'column': 'id', 'field': PrimaryKeyField },
        { 'column': 'name', 'field': CharField },
        { 'column': 'type', 'field': ForeignKeyField },
        { 'column': 'foreign', 'field': CharField },
        { 'column': 'unique', 'field': BooleanField },
        { 'column': 'description', 'field': CharField },
        { 'column': 'label', 'field': CharField }
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


@pytest.mark.parametrize('item', [
    Users(name='dummy', email='email', password='passwd', rank=1),
    Types(name='mytype', enabled=0),
])
def test_items_io(item):
    """
    Verifies that is possible to create and delete items.
    """
    item.save()
    assert getattr(item, 'id') != None
    item.delete_instance()
