# -*- coding: utf-8 -*-
"""
"""
import sys
sys.path.insert(0, "")
import json
import base64
import pytest


from peewee import FieldDescriptor, RelationDescriptor


from efesto.Models import Users, Types, Fields, AccessRules, EternalTokens
from efesto.Base import db
from efesto.Resources import *
from efesto.Auth import *


@pytest.fixture
def app():
    application = falcon.API()
    return application


@pytest.fixture(scope='module')
def dummy_user(request):
    db.connect()
    dummy = Users(name='dummy', email='mail', password='sample', rank=0)
    dummy.save()

    def teardown():
        dummy.delete_instance()
    request.addfinalizer(teardown)
    return dummy


@pytest.fixture
def auth_string():
    token = "%s:" % (generate_token(decode=True, user='myuser'))
    string64 = base64.b64encode( token.encode("latin-1") ).decode("latin-1")
    return "Basic %s" % (string64)


@pytest.mark.parametrize('model', [Users, Types, Fields, AccessRules, EternalTokens])
@pytest.mark.parametrize('method',
    ['on_get', 'on_post', 'model']
)
def test_make_collection(model, method):
    """
    Tests whether make_collection can correctly generate a resource.
    """
    resource = make_collection(model)
    assert hasattr(resource, method)


@pytest.mark.parametrize('model', [Users, Types, Fields, AccessRules, EternalTokens])
def test_make_collection_get(client, app, model):
    """
    Tests the behaviour of a generated resource when a simple GET request is
    performed.
    """
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)
    response = client.get('/endpoint')
    assert response.status == falcon.HTTP_UNAUTHORIZED
    assert response.__dict__['headers']['www-authenticate'] != None


@pytest.mark.parametrize('model', [Users, Types, Fields, AccessRules, EternalTokens])
def test_make_collection_get_auth(client, app, auth_string, model):
    """
    Tests the behaviour of a generated resource when a GET request that includes
    a basic auth header is performed.
    """
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)

    response = client.get('/endpoint', headers={'authorization':auth_string})
    assert response.status == falcon.HTTP_OK
    assert len(json.loads(response.body)) == model.select().limit(20).count()


@pytest.mark.parametrize('test_args',
    [
        {'model': Users, 'data': {'name':'test', 'password':'passwd'} },
        {'model': Types, 'data':{'name': 'sometype', 'enabled':0} },
        {'model': Fields, 'data':{'name':'somefield', 'type':1}},
        {'model': AccessRules, 'data':{'user':1, 'level':5}}
    ]
)
def test_make_collection_post(client, app, test_args):
    """
    Tests the behaviour of a generated resource when a simple POST request is
    performed.
    """
    model = test_args['model']
    data = test_args['data']
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)
    response = client.post('/endpoint', data)
    assert response.status == falcon.HTTP_UNAUTHORIZED


@pytest.mark.parametrize('test_args', [
    {'model': Users, 'data': {'name':'test', 'password':'passwd', 'email':'mail', 'rank':1} },
    {'model': Types, 'data': {'name': 't_one', 'enabled':0} }
])
def test_make_collection_post_auth(client, app, auth_string, test_args):
    """
    Tests the behaviour of a generated resource when a POST request that includes
    a basic auth header is performed.
    """
    model = test_args['model']
    data = test_args['data']
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)

    response = client.post('/endpoint', data=data, headers={'authorization':auth_string})
    assert response.status == falcon.HTTP_CREATED
    body = json.loads(response.body)
    assert 'id' in body
    for key in data:
        assert key in body
    # teardown
    item = model.get( getattr(model, 'id') == int(body['id']))
    item.delete_instance()


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
def test_make_resource_not_found(client, app, auth_string, model, method):
    """
    Tests the behaviour of a generated resource when a GET or DELETE request that
    includes a basic auth header is performed.
    """
    resource = make_resource(model)()
    app.add_route('/endpoint/{id}', resource)
    if method == 'get':
        response = client.get('/endpoint/1234', headers={'authorization':auth_string})
    elif method == 'delete':
        response = client.delete('/endpoint/1234', headers={'authorization':auth_string})
    elif method == 'patch':
        response = client.patch('/endpoint/1234', headers={'authorization':auth_string}, body='')
    assert response.status == falcon.HTTP_NOT_FOUND


@pytest.mark.parametrize('model', [Users, Types, Fields, AccessRules, EternalTokens])
def test_make_resource_get_item(client, app, auth_string, model):
    """
    Tests the behaviour of a generated resource when a GET request that includes
    a basic auth header is performed and an item is retrieved.
    """
    item = model.get()
    resource = make_resource(model)()
    app.add_route('/endpoint/{id}', resource)
    response = client.get('/endpoint/%s' % (item.id), headers={'authorization':auth_string})
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


@pytest.mark.parametrize('model', [Users, Types, Fields, AccessRules, EternalTokens])
def test_make_resource_delete_item(client, app, auth_string, model):
    """
    Tests the behaviour of a generated resource when a DELETE request that
    includes a basic auth header is performed and an item is deleted.
    """
    item = model.get()
    item_id = item.id
    resource = make_resource(model)()
    app.add_route('/endpoint/{id}', resource)
    response = client.delete('/endpoint/%s' % (item_id), headers={'authorization':auth_string})
    assert response.status == falcon.HTTP_NO_CONTENT
    try:
        deleted = model.get( getattr(model, 'id') == item_id)
    except:
        deleted = True
    assert deleted == True


@pytest.mark.parametrize('data', [
    {'username':'user'}, {'password': 'passwd'}, {'somevar':'var'}
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
