# -*- coding: utf-8 -*-
"""
   The Eefesto Resources module.

   Copyright (C) 2016 Jacopo Cascioli

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import json
from datetime import datetime
import falcon


from peewee import FieldDescriptor, RelationDescriptor
from .Auth import (authenticate_by_password, authenticate_by_token,
                   generate_token)
from .Models import EternalTokens, Users


def make_collection(model):
    """
    The make_collection function acts as generator of collection for models.
    """
    def on_get(self, request, response):
        user = None
        if request.auth:
            user = authenticate_by_token(request.auth)

        if user is None:
            raise falcon.HTTPUnauthorized('Login required', 'Please login',
                                          ['Basic realm="Login Required"'])
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

        order = None
        if 'order_by' in request.params:
            order = request.params['order_by']

        fields = ['id']
        if '_fields' in request.params:
            if request.params['_fields'] != 'all':
                fields = request.params['_fields'].split(',')
                fields.append('id')
            else:
                fields = 'all'

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

        if order is not None:
            if order[0] == '<':
                query = query.order_by(getattr(self.model, order[1:]).desc())
            elif order[0] == '>':
                query = query.order_by(getattr(self.model, order[1:]).asc())
            else:
                query = query.order_by(getattr(self.model, order).asc())

        count = query.count()

        body = []
        for i in query.paginate(page, items):
            if user.can('read', i):
                item = {}
                for column in columns:
                    if column in fields or fields == 'all':
                        item[column] = getattr(i, column)
                body.append(item)

        if len(body) == 0:
            raise falcon.HTTPNotFound()

        def json_serial(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError('Type not serializable')
        response.body = json.dumps(body, default=json_serial)

        if count > items:
            domain = '{}://{}?page=%s&items={}'.format(request.protocol,
                                                       request.host, items)
            last_page = int(count / items)

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
        request._parse_form_urlencoded()
        user = None
        if request.auth:
            user = authenticate_by_token(request.auth)

        if user is None:
            raise falcon.HTTPUnauthorized('Login required', 'Please login',
                                          ['Basic realm="Login Required"'])

        user = Users.get(Users.name == user)

        new_item = self.model(**request.params)
        if user.can('read', new_item):
            new_item.save()
            response.status = falcon.HTTP_CREATED
            response.body = json.dumps(new_item.__dict__['_data'])
        else:
            raise falcon.HTTPForbidden('forbidden', 'forbidden')

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

        if user is None:
            raise falcon.HTTPUnauthorized('Login required', 'Please login',
                                          ['Basic realm="Login Required"'])
        user = Users.get(Users.name == user)

        try:
            item = self.model.get(getattr(self.model, 'id') == id)
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

            def json_serial(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError('Type not serializable')
            response.body = json.dumps(item_dict, default=json_serial)
        else:
            raise falcon.HTTPForbidden('forbidden', 'forbidden')

    def on_delete(self, request, response, id=0):
        user = None
        if request.auth:
            user = authenticate_by_token(request.auth)

        if user is None:
            raise falcon.HTTPUnauthorized('Login required', 'Please login',
                                          ['Basic realm="Login Required"'])
        user = Users.get(Users.name == user)

        try:
            item = self.model.get(getattr(self.model, 'id') == id)
        except:
            raise falcon.HTTPNotFound()

        if user.can('eliminate', item):
            item.delete_instance()
            response.status = falcon.HTTP_NO_CONTENT
        else:
            raise falcon.HTTPForbidden('forbidden', 'forbidden')

    def on_patch(self, request, response, id=0):
        user = None
        if request.auth:
            user = authenticate_by_token(request.auth)

        if user is None:
            raise falcon.HTTPUnauthorized('Login required', 'Please login',
                                          ['Basic realm="Login Required"'])
        user = Users.get(Users.name == user)

        try:
            item = self.model.get(getattr(self.model, 'id') == id)
        except:
            raise falcon.HTTPNotFound()

        if user.can('edit', item):
            stream = request.stream.read().decode('UTF-8')
            if len(stream) > 0:
                for i in stream.split('&'):
                    arg = i.split('=')
                    setattr(item, arg[0], arg[1])
                item.save()

            item_dict = {}
            for k in self.model.__dict__:
                if (
                    isinstance(self.model.__dict__[k], FieldDescriptor) and
                    not isinstance(self.model.__dict__[k], RelationDescriptor)
                ):
                    item_dict[k] = getattr(item, k)
            response.body = json.dumps(item_dict)
        else:
            raise falcon.HTTPForbidden('forbidden', 'forbidden')

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
        request._parse_form_urlencoded()
        if 'password' not in request.params or 'username' not in request.params:
            raise falcon.HTTPBadRequest('', '')

        authentication = authenticate_by_password(request.params['username'],
                                                  request.params['password'])
        if authentication is None:
            raise falcon.HTTPUnauthorized('Login required', 'Pleas login',
                                          ['Basic realm="Login Required"'])

        if 'token_name' in request.params:
            try:
                t = EternalTokens.get(
                    EternalTokens.name == request.params['token_name'],
                    EternalTokens.user == authentication.id
                ).token
            except:
                raise falcon.HTTPNotFound()
            token = generate_token(token=t)
        else:
            token = generate_token(user=request.params['username'])
        response.status = falcon.HTTP_OK
        response.body = json.dumps({'token': token})


class RootResource:
    """
    The RootResource resource handles requests made to the root endpoint.
    """
    def __init__(self, data):
        self.data = data

    def on_get(self, request, response):
        response.body = json.dumps(self.data)
