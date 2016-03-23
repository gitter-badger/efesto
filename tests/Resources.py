# -*- coding: utf-8 -*-
"""
"""
import sys
sys.path.insert(0, "")
import pytest


from efesto.Models import *
from efesto.Resources import *


@pytest.fixture
def app():
    application = falcon.API()
    return application


@pytest.mark.parametrize('model', [Users])
@pytest.mark.parametrize('method',
    ['on_get', 'on_post', 'on_patch', 'on_delete']
)
def test_make_resource(model, method):
    resource = make_resource(model)
    assert hasattr(resource, method)


@pytest.mark.parametrize('model', [Users])
def test_get(client, app, model):
    resource = make_resource(model)()
    app.add_route('/endpoint', resource)
    response = client.get('/endpoint')
    assert response.status == falcon.HTTP_UNAUTHORIZED


@pytest.mark.parametrize('test_args',
    [
        {'model': Users, 'data': {'name':'test', 'password':'passwd'} }
    ]
)
def test_post(client, app, test_args):
    model = test_args['model']
    data = test_args['data']
    resource = make_resource(model)()
    app.add_route('/endpoint', resource)
    response = client.post('/endpoint', data)
    assert response.status == falcon.HTTP_UNAUTHORIZED
