# -*- coding: utf-8 -*-
"""
    Resources
"""
import falcon
import json


from peewee import FieldDescriptor, RelationDescriptor


from .Models import EternalTokens
from .Auth import *


def make_collection(model):
    """
    The make_collection function acts as generator of collection for models.
    """
    def on_get(self, request, response):
        user = None
        if request.auth:
            user = authenticate_by_token(request.auth)

        if user == None:
            raise falcon.HTTPUnauthorized('Login required', 'You need to login', scheme='Basic realm="Login Required"')
        user = Users.get(Users.name == user)

        columns = []
        for i in self.model.__dict__:
            if isinstance(self.model.__dict__[i], FieldDescriptor):
                if not isinstance(self.model.__dict__[i], RelationDescriptor):
                    columns.append(i)

        params = {}
        for i in columns:
            if i in request.params:
                params[i] = request.params[i]

        page = 1
        if 'page' in request.params:
            page = int(request.params['page'])

        items = 20
        if 'items' in request.params:
            items = int(request.params['items'])

        query = self.model.select()
        for key, argument in params.items():
            if argument[0] == '<':
                query = query.where(getattr(self.model, key) <= argument[1:])
            elif argument[0] == '>':
                query = query.where(getattr(self.model, key) >= argument[1:])
            elif argument[0] == '!':
                query = query.where(getattr(self.model, key) != argument[1:])
            else:
                query = query.where(getattr(self.model, key) == argument)
        count = query.count()

        body = []
        for i in query.paginate(page, items):
            if user.can('read', i):
                item = {}
                for column in columns:
                    item[column] = getattr(i, column)
                body.append(item)

        if len(body) == 0:
            raise falcon.HTTPNotFound()
        response.body = json.dumps(body)

        if count > items:
            domain = "{}://{}?page=%s&items={}".format(request.protocol,
                request.host, items)
            last_page = int(count/items)

            if page != 1:
                prev_page = page - 1
                url = domain % (prev_page)
                response.add_link(url, rel='prev')

            if page != last_page:
                last_url = domain % (last_page)
                response.add_link(last_url, rel='last')
                next_page = page + 1
                if next_page != last_page:
                    next_url = domain % (next_page)
                    response.add_link(next_url, rel='next')


    def on_post(self, request, response):
        user = None
        if request.auth:
            user = authenticate_by_token(request.auth)

        if user == None:
            raise falcon.HTTPUnauthorized('Login required', 'You need to login', scheme='Basic realm="Login Required"')
        user = Users.get(Users.name == user)

        new_item = self.model(**request.params)
        if user.can('read', new_item):
            new_item.save()
            response.status = falcon.HTTP_CREATED
            response.body = json.dumps(new_item.__dict__['_data'])
        else:
            raise falcon.HTTPForbidden("forbidden", "forbidden")

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
            user = authenticate_by_token(request.auth)

        if user == None:
            raise falcon.HTTPUnauthorized('Login required', 'You need to login', scheme='Basic realm="Login Required"')
        user = Users.get(Users.name == user)

        try:
            item = self.model.get( getattr(self.model, 'id') == id )
        except:
            raise falcon.HTTPNotFound()

        if user.can('read', item):
            item_dict = {}
            for k in self.model.__dict__:
                if (
                    isinstance(self.model.__dict__[k], FieldDescriptor) and
                    not isinstance(self.model.__dict__[k], RelationDescriptor)
                ):
                    item_dict[k] = getattr(item, k)
            response.body = json.dumps(item_dict)
        else:
            raise falcon.HTTPForbidden("forbidden", "forbidden")


    def on_delete(self, request, response, id=0):
        user = None
        if request.auth:
            user = authenticate_by_token(request.auth)

        if user == None:
            raise falcon.HTTPUnauthorized('Login required', 'You need to login', scheme='Basic realm="Login Required"')

        try:
            item = self.model.get( getattr(self.model, 'id') == id )
        except:
            raise falcon.HTTPNotFound()

        item.delete_instance()
        response.status = falcon.HTTP_NO_CONTENT

    def on_patch(self, request, response, id=0):
        user = None
        if request.auth:
            user = authenticate_by_token(request.auth)

        if user == None:
            raise falcon.HTTPUnauthorized('Login required', 'You need to login', scheme='Basic realm="Login Required"')

        try:
            item = self.model.get( getattr(self.model, 'id') == id )
        except:
            raise falcon.HTTPNotFound()


    attributes = {
        'model': model,
        'on_get': on_get,
        'on_patch': on_patch,
        'on_delete': on_delete
    }
    return type('mycollection', (object, ), attributes)


class TokensResource:
    """
    The TokensResource resource handles tokens requests.
    """
    def on_post(self, request, response):
        if not 'password' in request.params or not 'username' in request.params:
            raise falcon.HTTPBadRequest('', '')

        if 'eternal' in request.params and not 'token_name' in request.params:
            raise falcon.HTTPBadRequest('', '')

        authentication = authenticate_by_password(request.params['username'], request.params['password'])
        if authentication == None:
            raise falcon.HTTPUnauthorized('Login required', 'You need to login', scheme='Basic realm="Login Required"')

        if 'eternal' in request.params and request.params['eternal'] == '1':
            try:
                t = EternalTokens.get( EternalTokens.name == request.params['token_name'], EternalTokens.user == authentication.id  ).token
            except:
                raise falcon.HTTPNotFound()
            token = generate_token(decode=True, token=t)
        else:
            token = generate_token(decode=True, user=request.params['username'])
        response.status = falcon.HTTP_OK
        response.body = json.dumps({'token': token})
