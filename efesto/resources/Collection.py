# -*- coding: utf-8 -*-
"""
   The Collection module.

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
import json
import falcon
from .Siren import hinder
from efesto.Auth import authenticate_by_token
from peewee import FieldDescriptor, ObjectIdDescriptor, RelationDescriptor


def model_columns(model):
    columns = []
    for i in model.__dict__:
        if isinstance(model.__dict__[i], FieldDescriptor):
            if not isinstance(model.__dict__[i], RelationDescriptor):
                columns.append(i)

        if isinstance(model.__dict__[i], ObjectIdDescriptor):
            columns.append(i)
    return columns



def last_page(count, items):
    pages = int(count / items) + 1
    return pages


def build_embeds(params):
    if 'embeds' in params:
        if type(params['embeds']) is str:
            return [params['embeds']]
        return params['embeds']
    return []


def build_fields(params):
    if '_fields' in params:
        fields = params['_fields']
        if type(fields) is str:
            if fields == 'all':
                return fields
            return ['id', fields]
        fields.append('id')
        return fields
    return ['id']


def build_query(model, params):
    query = model.select()
    for key, argument in params.items():
        if argument[0] == '<':
            query = query.where(getattr(model, key) <= argument[1:])
        elif argument[0] == '>':
            query = query.where(getattr(model, key) >= argument[1:])
        elif argument[0] == '!':
            query = query.where(getattr(model, key) != argument[1:])
        elif argument[0] == '-':
            query = query.where(getattr(model, key) >> None)
        else:
            query = query.where(getattr(model, key) == argument)
    return query


def build_item(columns, fields, currrent_item, embeds):
    item = {}
    for column in columns:
        if column in fields or fields == 'all':
            item[column] = getattr(currrent_item, column)
    for embed in embeds:
        column_to_embed = getattr(currrent_item, embed)
        item[embed] = getattr(column_to_embed, '_data')
    return item


def build_order(model, query, order):
    if order[0] == '<':
        query = query.order_by(getattr(model, order[1:]).desc())
    elif order[0] == '>':
        query = query.order_by(getattr(model, order[1:]).asc())
    else:
        query = query.order_by(getattr(model, order).asc())
    return query


def build_link_headers(request, response, count, items, page):
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


def on_get(self, request, response):
    user = None
    if request.auth:
        user = authenticate_by_token(request.auth)

    if user is None:
        raise falcon.HTTPUnauthorized('Login required', 'Please login',
                                      ['Basic realm="Login Required"'])

    columns = model_columns(self.model)
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

    embeds = build_embeds(request.params)
    fields = build_fields(request.params)

    query = build_query(self.model, params)
    if order is not None:
        query = build_order(self.model, query, order)
    count = query.count()

    body = []
    for i in query.paginate(page, items):
        if user.can('read', i):
            item = build_item(columns, fields, i, embeds)
            body.append(item)

    if len(body) == 0:
        response.status = falcon.HTTP_NO_CONTENT
        return response

    def json_serial(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError('Type not serializable')
    pages = last_page(count, items)
    s = hinder(body, path=request.path, page=page, last_page=pages)
    response.body = json.dumps(s, default=json_serial)

    if count > items:
        build_link_headers(request, response, count, items, page)


def on_post(self, request, response):
    request._parse_form_urlencoded()
    user = None
    if request.auth:
        user = authenticate_by_token(request.auth)

    if user is None:
        raise falcon.HTTPUnauthorized('Login required', 'Please login',
                                      ['Basic realm="Login Required"'])

    if 'owner' not in request.params:
        request.params['owner'] = user.id
    new_item = self.model(**request.params)
    if user.can('read', new_item):
        with db.atomic():
            try:
                new_item.save()
            except:
                raise falcon.HTTPInternalServerError('Internal error', 'The \
    requested operation cannot be completed')
        response.status = falcon.HTTP_CREATED
        path = '{}/{}'.format(request.path, new_item.id)
        s = hinder(new_item.__dict__['_data'], path=path)
        response.body = json.dumps(s)
    else:
        raise falcon.HTTPForbidden('Forbidden access', 'You do not have the \
required permissions for this action')




def make_collection(model):
    """
    The make_collection function acts as generator of collection for models.
    """
    attributes = {
        'model': model,
        'on_get': on_get,
        'on_post': on_post
    }
    return type('mycollection', (object, ), attributes)