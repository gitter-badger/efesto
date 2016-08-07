# -*- coding: utf-8 -*-
"""
"""
import base64
import sys

from efesto.Auth import generate_token
from efesto.Models import (AccessRules, EternalTokens, Fields, Types, Users,
                           make_model)
import falcon
import pytest


sys.path.insert(0, '')


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
def dummy_type(request):
    custom_type = Types(name='mycustomtype', enabled=1)
    custom_type.save()

    def teardown():
        custom_type.delete_instance()
    request.addfinalizer(teardown)
    return custom_type


@pytest.fixture
def custom_field(request, dummy_type):
    custom_field = Fields(name='f', type=dummy_type.id, field_type='string')
    custom_field.save()

    def teardown():
        custom_field.delete_instance()
    request.addfinalizer(teardown)
    return custom_field


@pytest.fixture
def complex_type(request):
    new_type = Types(name='mytype', enabled=0)
    new_type.save()

    def teardown():
        new_type.delete_instance()
    request.addfinalizer(teardown)
    return new_type


@pytest.fixture
def complex_fields(request, complex_type):
    str_field = Fields(name='strfield', type=complex_type.id,
                       field_type='string')
    str_field.save()
    int_field = Fields(name='intfield', type=complex_type.id, field_type='int')
    int_field.save()
    date_field = Fields(name='datefield', type=complex_type.id,
                        field_type='date')
    date_field.save()
    nfield = Fields(name='nfield', type=complex_type.id, field_type='string',
                    nullable=True)
    nfield.save()
    ufield = Fields(name='ufield', type=complex_type.id, field_type='string',
                    unique=True)
    ufield.save()

    def teardown():
        str_field.delete_instance()
        int_field.delete_instance()
        date_field.delete_instance()
        nfield.delete_instance()
        ufield.delete_instance()
    request.addfinalizer(teardown)
    return str_field, int_field, date_field, nfield, ufield


@pytest.fixture
def complex_item(request, complex_type, complex_fields, dummy_admin):
    complex_type.enabled = 1
    complex_type.save()
    item = make_model(complex_type)(strfield='test', intfield=10,
                                    datefield='2016-04-20', ufield='val',
                                    owner=dummy_admin.id)
    item.save()

    def teardown():
        item.delete_instance()
    request.addfinalizer(teardown)
    return item


@pytest.fixture
def token(request, dummy_admin):
    new_token = EternalTokens(name='mytoken', user=dummy_admin.id,
                              token='token')
    new_token.save()

    def teardown():
        new_token.delete_instance()
    request.addfinalizer(teardown)
    return new_token


@pytest.fixture
def user_token(request, dummy_user):
    new_token = EternalTokens(name='mytoken', user=dummy_user.id,
                              token='token')
    new_token.save()

    def teardown():
        new_token.delete_instance()
    request.addfinalizer(teardown)
    return new_token


@pytest.fixture(params=['client', 'server'])
def admin_auth(request, token, dummy_admin):
    if request.param == 'client':
        token_string = '%s:' % (generate_token(decode=True,
                                user=dummy_admin.name))
    else:
        token_string = '%s:' % (generate_token(decode=True, token=token.token))
    encoded_token = token_string.encode('latin-1')
    string64 = base64.b64encode(encoded_token).decode('latin-1')
    return 'Basic %s' % (string64)


@pytest.fixture(params=['client', 'server'])
def user_auth(request, user_token, dummy_user):
    if request.param == 'client':
        token_string = '%s:' % (generate_token(decode=True,
                                               user=dummy_user.name))
    else:
        token_string = '%s:' % (generate_token(decode=True,
                                               token=user_token.token))
    encoded_token = token_string.encode('latin-1')
    string64 = base64.b64encode(encoded_token).decode('latin-1')
    return 'Basic %s' % (string64)


@pytest.fixture(params=[
    {'model': Users, 'args': {'name': 'u', 'email': 'mail', 'password': 'p',
                              'rank': 1}},
    {'model': Types, 'args': {'name': 'mytype', 'enabled': 0}},
    {'model': AccessRules, 'args': {'level': 1}},
    {
        'model': Fields, 'args': {'name': 'f', 'field_type': 'string'},
        'parent': Types, 'parent_args': {'name': 't2', 'enabled': 0},
        'parent_field': 'type'
    },
    {
        'model': EternalTokens, 'args': {'name': 'mytoken', 'token': ''},
        'parent': Users, 'parent_args': {'name': 'u2', 'email': 'mail',
                                         'password': 'p', 'rank': 1},
        'parent_field': 'user'
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
