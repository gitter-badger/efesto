# -*- coding: utf-8 -*-
"""
"""
import sys
sys.path.insert(0, "")
import re
import json
import falcon
import pytest

from peewee import FieldDescriptor, RelationDescriptor


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
def pagination_items(request):
    model = Users
    items = 4
    items_list = []
    for i in range(1, items):
        name = 'u%s' % (10-i)
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


def test_make_collection_get_auth(client, app, admin_auth, item_with_model):
    """
    Tests the behaviour of a generated resource when a GET request that includes
    a basic auth header is performed.
    """
    model = item_with_model[1]
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)

    response = client.get('/endpoint', headers={'authorization':admin_auth})
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


def test_make_collection_make_model_get_auth(client, app, admin_auth,
        dummy_type, dummy_admin, custom_field):
    """
    Verifies that make_collection can use make_model's generated models and
    return a 200 when auth is sent.
    """
    model = make_model(dummy_type)
    item = model(owner=dummy_admin, f='someval')
    item.save()
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)
    response = client.get('/endpoint', headers={'authorization':admin_auth})
    assert response.status == falcon.HTTP_OK
    assert len(json.loads(response.body)) == model.select().limit(20).count()
    # teardown
    item.delete_instance()

def test_make_collection_response_fields(client, app, admin_auth, item_with_model):
    """
    Verifies that make_collection generated endpoints return only the item id
    on GET requests.
    """
    model = item_with_model[1]
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)
    response = client.get('/endpoint', headers={'authorization':admin_auth})
    body = json.loads(response.body)
    for item in body:
        assert 'id' in item
        assert len(item.keys()) == 1


def test_make_collection_fields_argument(client, app, admin_auth, item_with_model):
    """
    Verifies that make_collection generated endpoints support the _fields
    argument to select returned fields.
    """
    model = item_with_model[1]
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)
    columns = []
    for i in model.__dict__:
        if isinstance(model.__dict__[i], FieldDescriptor):
            if not isinstance(model.__dict__[i], RelationDescriptor):
                columns.append(i)
    columns.remove('id')
    query = "_fields=%s" % (columns[0])
    url = '/endpoint?%s' % (query)
    response = client.get(url, headers={'authorization':admin_auth})
    body = json.loads(response.body)
    for item in body:
        assert columns[0] in item


def test_make_collection_fields_argument_all(client, app, admin_auth, item_with_model):
    """
    Verifies that the _fields argument support an 'all' value, returning all
    fields.
    """
    model = item_with_model[1]
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)
    response = client.get('/endpoint?_fields=all', headers={'authorization':admin_auth})
    columns = []
    for i in model.__dict__:
        if isinstance(model.__dict__[i], FieldDescriptor):
            if not isinstance(model.__dict__[i], RelationDescriptor):
                columns.append(i)
    body = json.loads(response.body)
    for item in body:
        for column in columns:
            assert column in item


@pytest.mark.parametrize('query', [
    'name=u7','rank=1', 'name=<u8', 'rank=1&name=!u3'
])
def test_make_collection_query(client, app, admin_auth, pagination_items, query):
    """
    Tests whether make_collection supports GET requests with search parameters.
    """
    resource = make_collection(Users)()
    app.add_route('/endpoint', resource)
    url = "/endpoint?%s" % (query)
    response = client.get(url, headers={'authorization':admin_auth})
    response_items = json.loads(response.body)
    params = query.split('&')
    for i in response_items:
        item = Users.get(Users.id == i['id'])
        for k in params:
            value = k.split('=')[1]
            if value[0] == '<':
                assert getattr(item, k.split('=')[0]) <= value[1:]
            elif value[0] == '>':
                assert getattr(item, k.split('=')[0]) >= value[1:]
            elif value[0] == '!':
                assert getattr(item, k.split('=')[0]) != value[1:]
            else:
                try:
                    value = int(value)
                except:
                    pass
                assert getattr(item, k.split('=')[0]) == value


@pytest.mark.parametrize('query_args', [{'abc':'rnd'}, {'43erg':1023}, {'one':'mix', 'me':10}])
def test_make_collection_query_ignored_args(client, app, admin_auth, item_with_model, query_args):
    """
    Verifies that non-supported query parameters are ignored.
    """
    model = item_with_model[1]
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)
    query_string = ''
    for key in query_args:
        query_string += '%s=%s&' % (key, query_args[key])
    query_string = query_string[:-1]
    url = "/endpoint?%s" % (query_string)
    response = client.get(url, headers={'authorization':admin_auth})
    assert response.status == falcon.HTTP_OK


@pytest.mark.parametrize('query', ['order_by=name', 'order_by=>name'])
def test_make_collection_order_arg_asc(client, app, admin_auth, pagination_items, query):
    resource = make_collection(Users)()
    app.add_route('/endpoint', resource)
    url = "/endpoint?%s" % (query)
    response = client.get(url, headers={'authorization':admin_auth})
    response_items = json.loads(response.body)
    previous = None
    for i in response_items:
        item = Users.get(Users.id == i['id'])
        if previous != None:
            assert item.name > previous
        previous = item.name


def test_make_collection_order_arg_desc(client, app, admin_auth, pagination_items):
    resource = make_collection(Users)()
    app.add_route('/endpoint', resource)
    url = "/endpoint?%s" % ('order_by=<name')
    response = client.get(url, headers={'authorization':admin_auth})
    response_items = json.loads(response.body)
    previous = None
    for i in response_items:
        item = Users.get(Users.id == i['id'])
        if previous != None:
            assert item.name < previous
        previous = item.name


def test_make_collection_query_pagination(client, app, admin_auth):
    """
    Verifies that make_collection supports pagination arguments.
    """
    new_user = Users(** {'name':'test', 'password':'passwd', 'email':'mail', 'rank':1})
    new_user.save()
    resource = make_collection(Users)()
    app.add_route('/endpoint', resource)
    response = client.get('/endpoint?page=2&items=1', headers={'authorization':admin_auth})
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
        admin_auth, args):
    """
    Verifies that Link headers are set correctly.
    """
    resource = make_collection(Users)()
    app.add_route('/endpoint', resource)
    url = "/endpoint?page=%s&items=%s" % (args['page'], args['items'])
    response = client.get(url, headers={'authorization':admin_auth})
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
def test_make_collection_post_auth(client, app, admin_auth, test_args):
    """
    Tests the behaviour of a generated resource when a POST request that includes
    a basic auth header is performed.
    """
    model = test_args['model']
    data = test_args['data']
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)

    response = client.post('/endpoint', data=data, headers={'authorization':admin_auth})
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
    Verifies make_collection's behaviour with a make_model generated model for
    non-authenticated POST requests.
    """
    model = make_model(dummy_type)
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)
    response = client.post('/endpoint', {'f':'text'})
    assert response.status == falcon.HTTP_UNAUTHORIZED


def test_make_collection_make_model_post_auth(client, app, dummy_admin,
    admin_auth, dummy_type, custom_field):
    """
    Verifies make_collection's behaviour with a make_model generated model for
    authenticated POST requests.
    """
    model = make_model(dummy_type)
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)
    data = {'owner':dummy_admin.id}
    data[custom_field.name] = 'someval'
    response = client.post('/endpoint', data=data, headers={'authorization':admin_auth})
    assert response.status == falcon.HTTP_CREATED
    body = json.loads(response.body)
    assert 'id' in body
    for key in data:
        assert key in body
    # teardown
    item = model.get( getattr(model, 'id') == int(body['id']))
    item.delete_instance()


def test_make_collection_access_rules_get(client, app, user_auth, item_with_model):
    """
    Verifies that make_collection applies access rules.
    """
    model = item_with_model[1]
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)
    response = client.get('/endpoint', headers={'authorization':user_auth})
    assert response.status == falcon.HTTP_NOT_FOUND


@pytest.mark.parametrize('test_args',
    [
        {'model': Users, 'data': {'name':'test', 'password':'passwd'} },
        {'model': Types, 'data':{'name': 'sometype', 'enabled':0} },
        {'model': Fields, 'data':{'name':'somefield', 'type':1}},
        {'model': AccessRules, 'data':{'user':1, 'level':5}}
    ]
)
def test_make_collection_access_rules_post(client, app, user_auth, test_args):
    """
    Verifies that make_collection correctly applies access rules to POST requests.
    """
    model = test_args['model']
    data = test_args['data']
    resource = make_collection(model)()
    app.add_route('/endpoint', resource)
    response = client.post('/endpoint', data=data, headers={'authorization':user_auth})
    assert response.status == falcon.HTTP_FORBIDDEN


def test_make_collection_serialization_get(client, app, admin_auth, complex_type,
        complex_fields, complex_item):
    complex_type.enabled = 1
    complex_type.save()
    model = make_model(complex_type)
    collection = make_collection(model)()
    app.add_route('/endpoint', collection)
    response = client.get('/endpoint', headers={'authorization':admin_auth})
    assert response.status == falcon.HTTP_OK
