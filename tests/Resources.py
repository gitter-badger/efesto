# -*- coding: utf-8 -*-
"""
"""
import sys
sys.path.insert(0, "")
import json
import base64
import pytest


from efesto.Models import Users, Types, Fields, AccessRules
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


@pytest.mark.parametrize('model', [Users, Types, Fields, AccessRules])
@pytest.mark.parametrize('method',
    ['on_get', 'on_post', 'model']
)
def test_make_collection(model, method):
    """
    Tests whether make_collection can correctly generate a resource.
    """
    resource = make_collection(model)
    assert hasattr(resource, method)


@pytest.mark.parametrize('model', [Users, Types, Fields, AccessRules])
def test_get(client, app, model):
    """
    Tests the behaviour of a generated resource when a simple GET request is
    performed.
    """
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)
    response = client.get('/endpoint')
    assert response.status == falcon.HTTP_UNAUTHORIZED
    assert response.__dict__['headers']['www-authenticate'] != None


@pytest.mark.parametrize('model', [Users, Types, Fields, AccessRules])
def test_get_auth(client, app, auth_string, model):
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
def test_post(client, app, test_args):
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
def test_post_auth(client, app, auth_string, test_args):
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
    resource = TokensResource()
    data = {'username':dummy_user.name, 'password':'sample'}
    app.add_route('/token', resource)
    response = client.post('/token', data)
    token = read_token( json.loads(response.body)['token'] )
    assert token['user'] == dummy_user.name
