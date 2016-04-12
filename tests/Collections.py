# -*- coding: utf-8 -*-
"""
"""
import sys
sys.path.insert(0, "")
import re
import base64
import json
import falcon
import pytest


from efesto.Base import db
from efesto.Models import Users, Types, Fields, AccessRules, EternalTokens, make_model
from efesto.Resources import make_collection
from efesto.Auth import generate_token


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
def dummy_admin(request):
    db.connect()
    dummy = Users(name='dummy', email='mail', password='sample', rank=10)
    dummy.save()

    def teardown():
        dummy.delete_instance()
    request.addfinalizer(teardown)
    return dummy


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
def token(request, dummy_admin):
    new_token = EternalTokens(name='mytoken', user=dummy_admin.id, token='token')
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
def auth_string(request, token, dummy_admin):
    if request.param == 'client':
        token_string = "%s:" % (generate_token(decode=True, user=dummy_admin.name))
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
                try:
                    value = int(value)
                except:
                    pass
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
