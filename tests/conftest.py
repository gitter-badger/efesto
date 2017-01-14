# -*- coding: utf-8 -*-
"""
"""
import base64
import os
import sys

from efesto.Auth import generate_token
from efesto.Models import (AccessRules, Fields, Types, Users,
                           make_model)
from itsdangerous import (TimedJSONWebSignatureSerializer as TimedSerializer)
import falcon
import pytest


sys.path.insert(0, '')


simple_items = [
    {'model': Users, 'args': {'name': 'u', 'email': 'mail', 'password': 'p',
                              'rank': 1, 'enabled': 1}},
    {'model': Types, 'args': {'name': 'mytype', 'enabled': 0}},
    {'model': AccessRules, 'args': {'level': 1}}
]
post_data = [
    {'model': Users, 'data': {'name': 'test', 'password': 'passwd'}},
    {'model': Types, 'data': {'name': 'sometype', 'enabled': 0}},
    {'model': Fields, 'data': {'name': 'somefield', 'type': 1}},
    {'model': AccessRules, 'data': {'user': 1, 'level': 5}}
]


def pytest_namespace():
    return {'simple_items': simple_items, 'post_data': post_data,
            'build_field': build_field}


def build_auth_header(request, token, user):
    """
    Builds an HTTP basic auth header for thte given user or token.
    """
    if request.param == 'client':
        generated_token = generate_token(decode=True, user=user.name)
    else:
        generated_token = generate_token(decode=True, token=token.token)
    token_string = ':{}'.format(generated_token)
    encoded_token = token_string.encode('latin-1')
    string64 = base64.b64encode(encoded_token).decode('latin-1')
    return 'Basic %s' % (string64)


def build_user(request, name, rank):
    """
    Builds an user with the specified name and rank.
    """
    user = Users(name=name, email='mail', password='sample', rank=rank,
                 enabled=1)
    user.save()

    def teardown():
        user.delete_instance()
    request.addfinalizer(teardown)
    return user


def build_type(request, name, enabled):
    """
    Builds a custom type with the given name and status.
    """
    custom_type = Types(name=name, enabled=enabled)
    custom_type.save()

    def teardown():
        custom_type.delete_instance()
    request.addfinalizer(teardown)
    return custom_type


def build_field(request, name, type_id, field_type, unique=None,
                nullable=None):
    custom_field = Fields(name=name, type=type_id, field_type=field_type,
                          unique=unique, nullable=nullable)
    custom_field.save()

    def teardown():
        custom_field.delete_instance()
    request.addfinalizer(teardown)
    return custom_field


def build_token(user):
    signed_token = TimedSerializer('secret', expires_in=600)
    return s.dumps({user: user}).decode('UTF-8')


@pytest.fixture
def app():
    application = falcon.API()
    return application


@pytest.fixture
def config_file(request):
    name = 'test.cfg'
    f = open(name, 'w')
    f.close()

    def teardown():
        os.remove(name)
    request.addfinalizer(teardown)
    return name


@pytest.fixture(scope='session')
def dummy_admin(request):
    return build_user(request, 'dummyadmin', 10)


@pytest.fixture(scope='module')
def dummy_user(request):
    return build_user(request, 'dummyuser', 0)


@pytest.fixture(scope='session')
def disabled_user(request):
    user = build_user(request, 'disabled_user', 0)
    user.enabled = 0
    user.save()
    return user


@pytest.fixture
def dummy_type(request):
    return build_type(request, 'mycustomtype', 1)


@pytest.fixture
def custom_field(request, dummy_type):
    return build_field(request, 'f', dummy_type.id, 'string')


@pytest.fixture
def complex_type(request):
    return build_type(request, 'mytype', 0)


@pytest.fixture
def complex_fields(request, complex_type):
    str_field = build_field(request, 'strfield', complex_type.id, 'string')
    int_field = build_field(request, 'intfield', complex_type.id, 'int')
    float_field = build_field(request, 'floatfield', complex_type.id, 'float')
    date_field = build_field(request, 'datefield', complex_type.id, 'date')
    nfield = build_field(request, 'nfield', complex_type.id, 'string',
                         nullable=True)
    ufield = build_field(request, 'ufield', complex_type.id, 'string',
                         unique=True)
    return str_field, int_field, float_field, date_field, nfield, ufield


@pytest.fixture
def referencing_type(request):
    return build_type(request, 'autotype', 0)


@pytest.fixture
def referencing_fields(request, referencing_type):
    name = build_field(request, 'name', referencing_type.id, 'string')
    reference = build_field(request, 'parent', referencing_type.id, 'autotype')
    return name, reference


@pytest.fixture
def complex_item(request, complex_type, complex_fields, dummy_admin):
    complex_type.enabled = 1
    complex_type.save()
    item = make_model(complex_type)(strfield='test', intfield=10,
                                    floatfield=3.2, datefield='2016-04-20',
                                    ufield='val', owner=dummy_admin.id)
    item.save()

    def teardown():
        item.delete_instance()
    request.addfinalizer(teardown)
    return item


@pytest.fixture
def token(request, dummy_admin):
    return build_token(dummy_admin)


@pytest.fixture
def user_token(request, dummy_user):
    return build_token(dummy_user)


@pytest.fixture
def disabled_token(request, disabled_user):
    return build_token(disabled_user)


@pytest.fixture(params=['client', 'server'])
def admin_auth(request, token, dummy_admin):
    return build_auth_header(request, token, dummy_admin)


@pytest.fixture(params=['client', 'server'])
def user_auth(request, user_token, dummy_user):
    return build_auth_header(request, user_token, dummy_user)


@pytest.fixture(scope='function', params=[
    {'model': Users, 'args': {'name': 'u', 'email': 'mail', 'password': 'p',
                              'rank': 1, 'enabled': 1}},
    {'model': Types, 'args': {'name': 'mytype', 'enabled': 0}},
    {'model': AccessRules, 'args': {'level': 1}},
    {
        'model': Fields, 'args': {'name': 'f', 'field_type': 'string'},
        'parent': Types, 'parent_args': {'name': 't2', 'enabled': 0},
        'parent_field': 'type'
    }
])
def item_with_model(request):
    model = request.param['model']
    item_dict = request.param['args']
    if 'parent' in request.param:
        parent_model = request.param['parent']
        parent_item = parent_model(**request.param['parent_args'])
        parent_item.save()
        item_dict[request.param['parent_field']] = parent_item.id
    item = model(**item_dict)
    item.save()

    def teardown():
        item.delete_instance()
        if 'parent' in request.param:
            parent_item.delete_instance()
    request.addfinalizer(teardown)
    return item, model
