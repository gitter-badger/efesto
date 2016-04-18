# -*- coding: utf-8 -*-
"""
"""
import sys
sys.path.insert(0, "")
import falcon
import pytest
import base64


from efesto.Models import Users, EternalTokens, Types, AccessRules, Fields
from efesto.Auth import generate_token


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
def token(request, dummy_admin):
    new_token = EternalTokens(name='mytoken', user=dummy_admin.id, token='token')
    new_token.save()
    def teardown():
        new_token.delete_instance()
    request.addfinalizer(teardown)
    return new_token


@pytest.fixture
def user_token(request, dummy_user):
    new_token = EternalTokens(name='mytoken', user=dummy_user.id, token='token')
    new_token.save()
    def teardown():
        new_token.delete_instance()
    request.addfinalizer(teardown)
    return new_token


@pytest.fixture(params=['client', 'server'])
def admin_auth(request, token, dummy_admin):
    if request.param == 'client':
        token_string = "%s:" % (generate_token(decode=True, user=dummy_admin.name))
    else:
        token_string = "%s:" % (generate_token(decode=True, token=token.token))
    string64 = base64.b64encode( token_string.encode("latin-1") ).decode("latin-1")
    return "Basic %s" % (string64)


@pytest.fixture(params=['client', 'server'])
def user_auth(request, user_token, dummy_user):
    if request.param == 'client':
        token_string = "%s:" % (generate_token(decode=True, user=dummy_user.name))
    else:
        token_string = "%s:" % (generate_token(decode=True, token=user_token.token))
    string64 = base64.b64encode( token_string.encode("latin-1") ).decode("latin-1")
    return "Basic %s" % (string64)


@pytest.fixture(params=[
    {'model':Users, 'args':{'name':'u', 'email':'mail', 'password':'p', 'rank':1} },
    {'model':Types, 'args': {'name':'mytype', 'enabled':0} },
    {'model':AccessRules, 'args': {'level': 1} },
    {
        'model':Fields, 'args': {'name':'f', 'field_type':'string'},
        'parent':Types, 'parent_args':{'name':'t2', 'enabled':0},
        'parent_field':'type'
    },
    {
        'model':EternalTokens, 'args':{'name':'mytoken', 'token':''},
        'parent': Users, 'parent_args':{'name':'u2', 'email':'mail',
        'password':'p', 'rank':1}, 'parent_field':'user'
    }
])
def item_with_model(request):
    model = request.param['model']
    item_dict = request.param['args']
    if 'parent' in request.param:
        parent_model = request.param['parent']
        parent_item = parent_model(**request.param['parent_args'])
        parent_item.save()
        item_dict[ request.param['parent_field'] ] = parent_item.id
    item = model(**item_dict)
    item.save()
    def teardown():
        item.delete_instance()
        if 'parent' in request.param:
            parent_item.delete_instance()
    request.addfinalizer(teardown)
    return item, model
