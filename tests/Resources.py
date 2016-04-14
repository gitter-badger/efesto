# -*- coding: utf-8 -*-
"""
"""
import sys
sys.path.insert(0, "")
import json
import falcon
import pytest


from peewee import FieldDescriptor, RelationDescriptor


from efesto.Models import Users, Types, Fields, AccessRules, EternalTokens, make_model
from efesto.Base import db
from efesto.Resources import make_resource, TokensResource
from efesto.Auth import generate_token, read_token


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


@pytest.mark.parametrize('model', [Users, Types, Fields, AccessRules, EternalTokens])
@pytest.mark.parametrize('method',
    ['on_get', 'on_patch', 'on_delete', 'model']
)
def test_make_resource(model, method):
    """
    Tests whether make_resource can correctly generate a resource.
    """
    resource = make_resource(model)
    assert hasattr(resource, method)


@pytest.mark.parametrize('model', [Users, Types, Fields, AccessRules, EternalTokens])
@pytest.mark.parametrize('method', ['get', 'delete', 'patch'])
def test_make_resource_unathorized(client, app, model, method):
    """
    Tests the behaviour of a generated resource when a GET or DELETE request is
    performed.
    """
    resource = make_resource(model)()
    app.add_route('/endpoint/{id}', resource)
    if method == 'get':
        response = client.get('/endpoint/1')
    elif method == 'delete':
        response = client.delete('/endpoint/1')
    elif method == 'patch':
        response = client.patch('/endpoint/1', body='')
    assert response.status == falcon.HTTP_UNAUTHORIZED
    assert response.__dict__['headers']['www-authenticate'] != None


@pytest.mark.parametrize('model', [Users, Types, Fields, AccessRules, EternalTokens])
@pytest.mark.parametrize('method', ['get', 'patch', 'delete'])
def test_make_resource_not_found(client, app, admin_auth, model, method):
    """
    Tests the behaviour of a generated resource when a GET or DELETE request that
    includes a basic auth header is performed.
    """
    resource = make_resource(model)()
    app.add_route('/endpoint/{id}', resource)
    if method == 'get':
        response = client.get('/endpoint/1234', headers={'authorization':admin_auth})
    elif method == 'delete':
        response = client.delete('/endpoint/1234', headers={'authorization':admin_auth})
    elif method == 'patch':
        response = client.patch('/endpoint/1234', headers={'authorization':admin_auth}, body='')
    assert response.status == falcon.HTTP_NOT_FOUND


@pytest.mark.parametrize('item_dict', [
    {'model': Users, 'args': {'name':'dummy_user', 'email':'email', 'password':'passwd', 'rank':1}},
    {'model': Types, 'args': {'name':'mytype', 'enabled':0}},
    {'model': AccessRules, 'args': {'level': 1}}
])
def test_make_resource_get_item(client, app, admin_auth, item_dict):
    """
    Tests the behaviour of a generated resource when a GET request that includes
    a basic auth header is performed and an item is retrieved.
    """
    # setup
    model = item_dict['model']
    new_item = model(**item_dict['args'])
    new_item.save()
    # test
    item = model.get()
    resource = make_resource(model)()
    app.add_route('/endpoint/{id}', resource)
    response = client.get('/endpoint/%s' % (item.id), headers={'authorization':admin_auth})
    assert response.status == falcon.HTTP_OK

    model_fields = []
    attrs = model.__dict__
    for k in attrs:
        if (
            isinstance(attrs[k], FieldDescriptor) and
            not isinstance(attrs[k], RelationDescriptor)
        ):
            model_fields.append(k)

    body = json.loads(response.body)
    for i in model_fields:
        assert body[i] == getattr(item, i)
    # teardown
    new_item.delete_instance()


def test_make_resource_get_fields():
    raise NotImplemented("Not implemented!")


def test_make_resource_get_tokens():
    raise NotImplemented("Not implemented!")


@pytest.mark.parametrize('method',
    ['on_get', 'on_patch', 'on_delete', 'model']
)
def test_make_resource_make_model(client, app, dummy_type, custom_field, method):
    """
    Tests whether make_resource can correctly generate a resource using
    make_model.
    """
    model = make_model(dummy_type)
    resource = make_resource(model)
    assert hasattr(resource, method)


@pytest.mark.parametrize('item_dict', [
    {'model': Users, 'args': {'name':'dummy_user', 'email':'email', 'password':'passwd', 'rank':1}},
    {'model': Types, 'args': {'name':'mytype', 'enabled':0}},
    {'model': AccessRules, 'args': {'level': 1}}
])
def test_make_resource_delete_item(client, app, admin_auth, item_dict):
    """
    Tests the behaviour of a generated resource when a DELETE request that
    includes a basic auth header is performed and an item is deleted.
    """
    # setup
    model = item_dict['model']
    item = model(**item_dict['args'])
    item.save()
    item_id = item.id
    # test
    resource = make_resource(model)()
    app.add_route('/endpoint/{id}', resource)
    response = client.delete('/endpoint/%s' % (item_id), headers={'authorization':admin_auth})
    assert response.status == falcon.HTTP_NO_CONTENT
    try:
        deleted = model.get( getattr(model, 'id') == item_id)
    except:
        deleted = True
    assert deleted == True


def test_make_resource_delete_fields():
    raise NotImplemented("Not implemented!")


def test_make_resource_delete_tokens():
    raise NotImplemented("Not implemented!")


@pytest.mark.parametrize('data', [
    {'username':'user'},
    {'password': 'passwd'},
    {'somevar':'var'},
    {'username':'user', 'password':'passwd', 'eternal': 1}
])
def test_tokens_resource_bad_request(client, app, data):
    """
    Verifies that TokensResource returns bad requests status when
    an incomplete POST request is made
    """
    resource = TokensResource()
    app.add_route('/token', resource)
    response = client.post('/token', data)
    assert response.status == falcon.HTTP_BAD_REQUEST


def test_tokens_resource_failure(client, app):
    """
    Verifies that sending wrong credentials to TokensResource results
    in a unauthorized response.
    """
    resource = TokensResource()
    data = {'username':'name', 'password':'passwd'}
    app.add_route('/token', resource)
    response = client.post('/token', data)
    assert response.status == falcon.HTTP_UNAUTHORIZED


def test_tokens_resource_passwd_failure(client, app, dummy_user):
    """
    Verifies that sending a wrong password to TokensResource results
    in a unauthorized response.
    """
    resource = TokensResource()
    data = {'username':dummy_user.name, 'password':'passwd'}
    app.add_route('/token', resource)
    response = client.post('/token', data)
    assert response.status == falcon.HTTP_UNAUTHORIZED


def test_tokens_resource(client, app, dummy_user):
    """
    Verifies that TokensResource returns a token when valid credentials
    are set.
    """
    resource = TokensResource()
    data = {'username':dummy_user.name, 'password':'sample'}
    app.add_route('/token', resource)
    response = client.post('/token', data)
    assert response.status == falcon.HTTP_OK
    assert 'token' in json.loads(response.body)


def test_tokens_resource_valid_token(client, app, dummy_user):
    """
    Verifies the contents of the token.
    """
    resource = TokensResource()
    data = {'username':dummy_user.name, 'password':'sample'}
    app.add_route('/token', resource)
    response = client.post('/token', data)
    token = read_token( json.loads(response.body)['token'] )
    assert token['user'] == dummy_user.name


def test_tokens_resource_eternal_not_found(client, app, dummy_user):
    """
    Verfies that when a requested token is not found a 404 error is returned.
    """
    resource = TokensResource()
    data = {'username':dummy_user.name, 'password':'sample', 'eternal':1, 'token_name': 'blah'}
    app.add_route('/token', resource)
    response = client.post('/token', data)
    assert response.status == falcon.HTTP_NOT_FOUND


def test_tokens_resource_eternal(client, app, dummy_admin, token):
    """
    Verifies that a correct token request returns a valid token.
    """
    resource = TokensResource()
    data = {'username':dummy_admin.name, 'password':'sample', 'eternal':1, 'token_name': token.name}
    app.add_route('/token', resource)
    response = client.post('/token', data)
    response_token = read_token(json.loads(response.body)['token'])
    assert response_token['token'] == token.token
