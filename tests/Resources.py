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
from efesto.Resources import make_resource, TokensResource
from efesto.Auth import generate_token, read_token


@pytest.fixture(params=[
    {'model':Users, 'args':{'name':'ud', 'email':'mail', 'password':'p', 'rank':1} },
    {'model':Types, 'args': {'name':'mytype', 'enabled':0} },
    {'model':AccessRules, 'args': {'level': 1} },
    {
        'model':Fields, 'args': {'name':'f', 'field_type':'string'},
        'parent':Types, 'parent_args':{'name':'d2', 'enabled':0},
        'parent_field':'type'
    },
    {
        'model':EternalTokens, 'args':{'name':'mytoken', 'token':''},
        'parent': Users, 'parent_args':{'name':'ud2', 'email':'mail',
        'password':'p', 'rank':1}, 'parent_field':'user'
    }
])
def deletable_item(request):
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


def test_make_resource_get_item(client, app, admin_auth, item_with_model):
    """
    Tests the behaviour of a generated resource when a GET request that includes
    a basic auth header is performed and an item is retrieved.
    """
    item = item_with_model[0]
    model = item_with_model[1]
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


def test_make_resource_patch_item(client, app, admin_auth, item_with_model):
    """
    Tests the behaviour of a generated resource when a PATCH request that includes
    a basic auth header is performed and an item is retrieved.
    """
    item = item_with_model[0]
    model = item_with_model[1]
    resource = make_resource(model)()
    app.add_route('/endpoint/{id}', resource)
    body = ''
    if model == Users:
        body = 'email=somrandommail&rank=2'
    elif model == Types:
        body = 'enabled=1'
    elif model == AccessRules:
        body = 'level=2&rank=3'
    elif model == EternalTokens:
        body = 'name=patched!'
    elif model == Fields:
        body = 'name=megafield'
    response = client.patch('/endpoint/%s' % (item.id), body=body,headers={'authorization':admin_auth})
    assert response.status == falcon.HTTP_OK
    check = {}
    for i in body.split('&'):
        arg = i.split('=')
        check[arg[0]] = arg[1]
    response_body = json.loads(response.body)
    for k in check:
        assert check[k] == response_body[k]


def test_make_resource_delete_item(client, app, admin_auth, deletable_item):
    """
    Tests the behaviour of a generated resource when a DELETE request that
    includes a basic auth header is performed and an item is deleted.
    """
    # setup
    model = deletable_item[1]
    item = deletable_item[0]
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


def test_make_resource_make_model_get(client, app, admin_auth,
        dummy_type, dummy_admin, custom_field):
    """
    Verifies that make_resource can use make_model's generated models and
    return a 200 when auth is sent.
    """
    model = make_model(dummy_type)
    item = model(owner=dummy_admin, f='someval')
    item.save()
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


def test_make_resource_make_model_patch(client, app, admin_auth, custom_field,
        dummy_type, dummy_admin):
    model = make_model(dummy_type)
    item = model(owner=dummy_admin, f='someval')
    item.save()
    resource = make_resource(model)()
    app.add_route('/endpoint/{id}', resource)
    body = '%s=myval' % (custom_field.name)
    check = {}
    check[custom_field.name] = 'myval'
    response = client.patch('/endpoint/%s' % (item.id), body=body,headers={'authorization':admin_auth})
    assert response.status == falcon.HTTP_OK
    response_body = json.loads(response.body)
    for k in check:
        assert check[k] == response_body[k]


def test_make_resource_make_model_delete(client, app, admin_auth, custom_field,
        dummy_type, dummy_admin):
    # setup
    model = make_model(dummy_type)
    item = model(owner=dummy_admin, f='someval')
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


def test_make_resource_access_rules_get(client, app, user_auth, item_with_model):
    """
    Verifies that make_resource correctly implements permissions on GET requests.
    """
    item = item_with_model[0]
    model = item_with_model[1]
    resource = make_resource(model)()
    app.add_route('/endpoint/{id}', resource)
    response = client.get('/endpoint/%s' % (item.id), headers={'authorization':user_auth})
    assert response.status == falcon.HTTP_FORBIDDEN


def test_make_resource_access_rules_patch(client, app, user_auth, item_with_model):
    """
    Verifies that make_resource correctly implements permissions on PATCH
    requests.
    """
    item = item_with_model[0]
    model = item_with_model[1]
    resource = make_resource(model)()
    body = ''
    if model == Users:
        body = 'email=somrandommail&rank=2'
    elif model == Types:
        body = 'enabled=1'
    elif model == AccessRules:
        body = 'level=2&rank=3'
    elif model == EternalTokens:
        body = 'name=patched!'
    elif model == Fields:
        body = 'name=megafield'
    app.add_route('/endpoint/{id}', resource)
    response = client.patch('/endpoint/%s' % (item.id), body=body,headers={'authorization':user_auth})
    assert response.status == falcon.HTTP_FORBIDDEN


def test_make_resource_access_rules_delete(client, app, user_auth, deletable_item):
    """
    Verifies that make_resource correctly implements permissions on DELETE requests.
    """
    item = deletable_item[0]
    model = deletable_item[1]
    item_id = item.id
    # test
    resource = make_resource(model)()
    app.add_route('/endpoint/{id}', resource)
    response = client.delete('/endpoint/%s' % (item_id), headers={'authorization':user_auth})
    assert response.status == falcon.HTTP_FORBIDDEN


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
