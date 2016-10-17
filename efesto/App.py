# -*- coding: utf-8 -*-
"""
    The Efesto App module.

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
import falcon
from falcon_cors import CORS

from .Base import config
from .Models import (AccessRules, EternalTokens, Fields, Types, Users,
                     make_model)
from .Resources import (RootResource, TokensResource, make_collection,
                        make_resource)
from .Version import __version__


cors = CORS(
    allow_all_origins=config.parser.getboolean('cors', 'all_origins'),
    allow_all_methods=config.parser.getboolean('cors', 'all_methods'),
    allow_all_headers=config.parser.getboolean('cors', 'all_headers'),
    allow_credentials_all_origins=config.parser.getboolean('cors',
                                                           'all_credentials')
)

if config.parser.getboolean('main', 'installed'):
    app = falcon.API(middleware=[cors.middleware])
    root_message = 'Running efesto %s' % (__version__)
    root_data = {'message': root_message}
    app.add_route('/', RootResource(root_data))

    for i in [['/users', Users], ['/types', Types], ['/fields', Fields],
              ['/rules', AccessRules], ['/tokens', EternalTokens]]:
        collection = make_collection(i[1])()
        resource = make_resource(i[1])()
        app.add_route(i[0], collection)
        app.add_route('%s/{id}' % i[0], resource)

    custom_types = Types.select().where(Types.enabled == True)
    for custom_type in custom_types:
        model = make_model(custom_type)
        model_name = getattr(model._meta, 'db_table')
        collection = make_collection(model)()
        resource = make_resource(model)()
        app.add_route('/%s' % (model_name), collection)
        app.add_route('/%s/{id}' % (model_name), resource)

    app.add_route('/auth', TokensResource())

    def error_serializer(req, exception):
        preferred = 'application/json'
        representation = exception.to_json()
        return (preferred, representation)
    app.set_error_serializer(error_serializer)
