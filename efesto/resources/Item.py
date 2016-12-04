# -*- coding: utf-8 -*-
"""
   The Item resource.

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
from datetime import datetime
import falcon
import json
from efesto.Auth import authenticate_by_token
from efesto.Siren import hinder
from peewee import FieldDescriptor, ObjectIdDescriptor, RelationDescriptor


def item_to_dictionary(model, item):
    item_dict = {}
    for k in model.__dict__:
        if isinstance(model.__dict__[k], FieldDescriptor):
            if not isinstance(model.__dict__[k], RelationDescriptor):
                item_dict[k] = getattr(item, k)
        if isinstance(model.__dict__[k], ObjectIdDescriptor):
            item_dict[k] = getattr(item, k)
    return item_dict


def on_get_resource(self, request, response, id=0):
    user = None
    if request.auth:
        user = authenticate_by_token(request.auth)

    if user is None:
        raise falcon.HTTPUnauthorized('Login required', 'Please login',
                                      ['Basic realm="Login Required"'])

    try:
        item = self.model.get(getattr(self.model, 'id') == id)
    except:
        description = 'The resource you are looking for does not exist'
        raise falcon.HTTPNotFound(title='Not found', description=description)

    if user.can('read', item):
        item_dict = item_to_dictionary(self.model, item)

        def json_serial(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError('Type not serializable')
        s = hinder(item_dict, path=request.path)
        response.body = json.dumps(s, default=json_serial)
    else:
        raise falcon.HTTPForbidden('Forbidden access', 'You do not have the \
required permissions for this action')


def on_patch_resource(self, request, response, id=0):
    user = None
    if request.auth:
        user = authenticate_by_token(request.auth)

    if user is None:
        raise falcon.HTTPUnauthorized('Login required', 'Please login',
                                      ['Basic realm="Login Required"'])

    try:
        item = self.model.get(getattr(self.model, 'id') == id)
    except:
        description = 'The resource you are looking for does not exist'
        raise falcon.HTTPNotFound(title='Not found', description=description)

    if user.can('edit', item):
        stream = request.stream.read().decode('UTF-8')
        parsed_stream = json.loads(stream)
        for key in parsed_stream:
            setattr(item, key, parsed_stream[key])
        with db.atomic():
            try:
                item.save()
            except:
                raise falcon.HTTPInternalServerError('Internal error', 'The \
    requested operation cannot be completed')
        item_dict = item_to_dictionary(self.model, item)
        s = hinder(item_dict, path=request.path)
        response.body = json.dumps(s)
    else:
        raise falcon.HTTPForbidden('Forbidden access', 'You do not have the \
required permissions for this action')


def on_delete_resource(self, request, response, id=0):
    user = None
    if request.auth:
        user = authenticate_by_token(request.auth)

    if user is None:
        raise falcon.HTTPUnauthorized('Login required', 'Please login',
                                      ['Basic realm="Login Required"'])

    try:
        item = self.model.get(getattr(self.model, 'id') == id)
    except:
        description = 'The resource you are looking for does not exist'
        raise falcon.HTTPNotFound(title='Not found', description=description)

    if user.can('eliminate', item):
        try:
            with db.atomic():
                item.delete_instance()
        except:
            raise falcon.HTTPInternalServerError('Internal error', 'The \
requested operation cannot be completed')
        response.status = falcon.HTTP_NO_CONTENT
    else:
        raise falcon.HTTPForbidden('Forbidden access', 'You do not have the \
required permissions for this action')



def make_resource(model):
    attributes = {
        'model': model,
        'on_get': on_get_resource,
        'on_patch': on_patch_resource,
        'on_delete': on_delete_resource
    }
    return type('mycollection', (object, ), attributes)
