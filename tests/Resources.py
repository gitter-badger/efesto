# -*- coding: utf-8 -*-
"""
"""
import sys
sys.path.insert(0, "")
import json
import base64
import pytest
import re


from peewee import FieldDescriptor, RelationDescriptor


from efesto.Models import Users, Types, Fields, AccessRules, EternalTokens, make_model
from efesto.Base import db
from efesto.Resources import *
from efesto.Auth import *


def parse_header_links(value):
    links = []
    replace_chars = " '\""
    for val in re.split(", *<", value):
        try:
            url, params = val.split(";", 1)
        except ValueError:
            url, params = val, ''

        link = {}
        link["url"] = url.strip("<> '\"")
        for param in params.split(";"):
            try:
                key, value = param.split("=")
            except ValueError:
                break

            link[key.strip(replace_chars)] = value.strip(replace_chars)
        links.append(link)
    return links


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
def token(request, dummy_user):
    new_token = EternalTokens(name='mytoken', user=dummy_user.id, token='token')
    new_token.save()
    def teardown():
        new_token.delete_instance()
    request.addfinalizer(teardown)
    return new_token


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


@pytest.fixture(params=['client', 'server'])
def auth_string(request, token):
    if request.param == 'client':
        token_string = "%s:" % (generate_token(decode=True, user='myuser'))
    else:
        token_string = "%s:" % (generate_token(decode=True, token=token.token))
    string64 = base64.b64encode( token_string.encode("latin-1") ).decode("latin-1")
    return "Basic %s" % (string64)


@pytest.fixture
def pagination_items(request):
    model = Users
    items = 4
    items_list = []
    for i in range(1, items):
        name = 'u%s' % (i)
        item_dict = {'name':name, 'email':'mail', 'password':'p', 'rank':1}
        item = model(**item_dict)
        item.save()
        items_list.append(item)

    def teardown():
        for i in items_list:
            i.delete_instance()
    request.addfinalizer(teardown)


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


def test_make_collection_make_model(client, app, dummy_type, custom_field):
    """
    Verifies that make_collection can use make_model's generated models and
    return a 401 to simple GET requests.
    """
    model = make_model(dummy_type)
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)
    response = client.get('/endpoint')
    assert response.status == falcon.HTTP_UNAUTHORIZED
    assert response.__dict__['headers']['www-authenticate'] != None


def test_make_collection_make_model_get_auth(client, app, auth_string,
        dummy_type, custom_field):
    """
    Verifies that make_collection can use make_model's generated models and
    return a 200 when auth is sent.
    """
    model = make_model(dummy_type)
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)
    response = client.get('/endpoint', headers={'authorization':auth_string})
    assert response.status == falcon.HTTP_OK
    assert len(json.loads(response.body)) == model.select().limit(20).count()


@pytest.mark.parametrize('query', [
    'name=u2','rank=2', 'name=<u3', 'rank=1&name=!u3'
])
def test_make_collection_query(client, app, auth_string, pagination_items, query):
    """
    Tests whether make_collection supports GET requests with search parameters.
    """
    resource = make_collection(Users)()
    app.add_route('/endpoint', resource)
    url = "/endpoint?%s" % (query)
    response = client.get(url, headers={'authorization':auth_string})
    response_items = json.loads(response.body)
    params = query.split('&')
    for i in response_items:
        for k in params:
            value = k.split('=')[1]
            if value[0] == '<':
                assert i[k.split('=')[0]] <= value[1:]
            elif value[0] == '>':
                assert i[k.split('=')[0]] >= value[1:]
            elif value[0] == '!':
                assert i[k.split('=')[0]] != value[1:]
            else:
                assert i[k.split('=')[0]] == value


@pytest.mark.parametrize('args', [
    {'model':Users, 'query':{'abc':'rnd'}},
    {'model':Types, 'query':{'43erg':1023} },
    {'model': AccessRules, 'query':{'potato':'valid'} }
])
def test_make_collection_query_ignored_args(client, app, auth_string, args):
    """
    Verifies that non-supported query parameters are ignored.
    """
    model = args['model']
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)
    query_string = ''
    for key in args['query']:
        query_string += '%s=%s&' % (key, args['query'][key])
    query_string = query_string[:-1]
    url = "/endpoint?%s" % (query_string)
    response = client.get(url, headers={'authorization':auth_string})
    assert response.status == falcon.HTTP_OK


def test_make_collection_query_pagination(client, app, auth_string):
    """
    Verifies that make_collection supports pagination arguments.
    """
    new_user = Users(** {'name':'test', 'password':'passwd', 'email':'mail', 'rank':1})
    new_user.save()
    resource = make_collection(Users)()
    app.add_route('/endpoint', resource)
    response = client.get('/endpoint?page=2&items=1', headers={'authorization':auth_string})
    items = json.loads(response.body)
    assert len(items) == 1
    assert items[0] == Users.select().paginate(2, 1).dicts()[0]
    new_user.delete_instance()


@pytest.mark.parametrize('args', [
    {'page':1, 'items': 1, 'rels':['next', 'last']},
    {'page':2, 'items':1, 'rels':['prev','next','last']},
    {'page':3, 'items':1, 'rels':['prev','last']},
    {'page':4, 'items':1, 'rels':['prev']}
])
def test_make_collection_pagination_headers(client, app, pagination_items,
        auth_string, args):
    """
    Verifies that Link headers are set correctly.
    """
    resource = make_collection(Users)()
    app.add_route('/endpoint', resource)
    url = "/endpoint?page=%s&items=%s" % (args['page'], args['items'])
    response = client.get(url, headers={'authorization':auth_string})
    assert 'Link' in response.headers
    parsed_header = parse_header_links(response.headers['Link'])
    rel_list = []
    for i in parsed_header:
        rel_list.append(i['rel'])
    for k in args['rels']:
        assert k in rel_list


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


def test_make_collection_make_model_post(client, app, dummy_type, custom_field):
    """
    """
    model = make_model(dummy_type)
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)
    response = client.post('/endpoint', {'f':'text'})
    assert response.status == falcon.HTTP_UNAUTHORIZED


def test_make_collection_make_model_post_auth(client, app, auth_string,
        dummy_type, custom_field):
    """
    """
    model = make_model(dummy_type)
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)
    response = client.post('/endpoint', {'f':'text'})
    assert response.status == falcon.HTTP_UNAUTHORIZED


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


@pytest.mark.parametrize('item_dict', [
    {'model': Users, 'args': {'name':'dummy_user', 'email':'email', 'password':'passwd', 'rank':1}},
    {'model': Types, 'args': {'name':'mytype', 'enabled':0}},
    {'model': AccessRules, 'args': {'level': 1}}
])
def test_make_resource_get_item(client, app, auth_string, item_dict):
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
def test_make_resource_delete_item(client, app, auth_string, item_dict):
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
    response = client.delete('/endpoint/%s' % (item_id), headers={'authorization':auth_string})
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


def test_tokens_resource_eternal(client, app, dummy_user, token):
    """
    Verifies that a correct token request returns a valid token.
    """
    resource = TokensResource()
    data = {'username':dummy_user.name, 'password':'sample', 'eternal':1, 'token_name': token.name}
    app.add_route('/token', resource)
    response = client.post('/token', data)
    response_token = read_token(json.loads(response.body)['token'])
    assert response_token['token'] == token.token
