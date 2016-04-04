# -*- coding: utf-8 -*-
"""
    Resources
"""
import falcon
import json


from peewee import FieldDescriptor, RelationDescriptor


from .Auth import *


def make_collection(model):
    """
    The make_collection function acts as generator of collection for models.
    """
    def on_get(self, request, response):
        user = None
        if request.auth:
            try:
                user = read_token(parse_auth_header(request.auth)[:-1])['user']
            except:
                user = None

        if user == None:
            raise falcon.HTTPUnauthorized('Login required', 'You need to login', scheme='Basic realm="Login Required"')

        body = []
        for i in self.model.select().limit(20).dicts():
            body.append(i)
        response.body = json.dumps(body)

    def on_post(self, request, response):
        user = None
        if request.auth:
            try:
                user = read_token(parse_auth_header(request.auth)[:-1])['user']
            except:
                user = None

        if user == None:
            raise falcon.HTTPUnauthorized('Login required', 'You need to login', scheme='Basic realm="Login Required"')

        new_item = self.model(**request.params)
        new_item.save()
        response.status = falcon.HTTP_CREATED
        response.body = json.dumps(new_item.__dict__['_data'])

    attributes = {
        'model': model,
        'on_get': on_get,
        'on_post': on_post
    }
    return type('mycollection', (object, ), attributes)


def make_resource(model):
    def on_get(self, request, response, id=0):
        user = None
        if request.auth:
            try:
                user = read_token(parse_auth_header(request.auth)[:-1])['user']
            except:
                user = None

        if user == None:
            raise falcon.HTTPUnauthorized('Login required', 'You need to login', scheme='Basic realm="Login Required"')

        try:
            item = self.model.get( getattr(self.model, 'id') == id )
        except:
            raise falcon.HTTPNotFound()

        item_dict = {}
        for k in self.model.__dict__:
            if (
                isinstance(self.model.__dict__[k], FieldDescriptor) and
                not isinstance(self.model.__dict__[k], RelationDescriptor)
            ):
                item_dict[k] = getattr(item, k)
        response.body = json.dumps(item_dict)


    attributes = {
        'model': model,
        'on_get': on_get,
        'on_patch': '',
        'on_delete': ''
    }
    return type('mycollection', (object, ), attributes)


class TokensResource:
    """
    The TokensResource resource handles tokens requests.
    """
    def on_post(self, request, response):
        if not 'password' in request.params or not 'username' in request.params:
            raise falcon.HTTPBadRequest('', '')

        authentication = authenticate(request.params['username'], request.params['password'])
        if authentication == False:
            raise falcon.HTTPUnauthorized('Login required', 'You need to login', scheme='Basic realm="Login Required"')

        token = generate_token(decode=True, user=request.params['username'])
        response.status = falcon.HTTP_OK
        response.body = json.dumps({'token': token})
