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
import falcon
from itsdangerous import TimedJSONWebSignatureSerializer as TimedSerializer
from efesto.Base import config
from efesto.models import Users


class TokensResource:
    """
    The TokensResource resource handles tokens requests.
    """
    def generate_token(expiration=600, **kwargs):
        s = TimedSerializer(config.parser.get('security', 'secret'),
                            expires_in=expiration)
        return s.dumps(kwargs).decode('UTF-8')

    def on_post(self, request, response):
        request._parse_form_urlencoded()
        if ('password' not in request.params or
                'username' not in request.params):
            raise falcon.HTTPBadRequest('Bad request',
                                        'A required parameter is missing')

        authentication = Users.authenticate_by_password(request.params['username'],
                                                  request.params['password'])
        if authentication is None:
            raise falcon.HTTPForbidden('Forbidden access',
                                       'The credentials provided are invalid')

        expiration = config.parser.getint('security', 'token_expiration')
        token = generate_token(expiration=expiration,
                               user=request.params['username'])
        response.status = falcon.HTTP_OK
        response.body = json.dumps({'token': token})
