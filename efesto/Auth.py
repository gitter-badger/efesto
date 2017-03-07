# -*- coding: utf-8 -*-
"""
    The Efesto authentication module.

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
import base64
from itsdangerous import (JSONWebSignatureSerializer as Serializer,
                          TimedJSONWebSignatureSerializer as TimedSerializer)

from .Base import config
from .models import Users


def read_token(token):
    """
    Reads a token. If the token contains a user parameter, the token is read
    with TimedSerializer.
    """
    s = Serializer(config.parser.get('security', 'secret'))
    result = s.loads(token)
    if 'user' in result:
        t = TimedSerializer(config.parser.get('security', 'secret'))
        return t.loads(token)
    else:
        return result


def parse_auth_header(auth_string):
    """
    Parses a basic auth header.
    """
    return base64.b64decode(auth_string.split()[1]).decode('latin-1')


def authenticate_by_token(auth_header):
    """
    Authenticates a user with a token or an eternal token.
    """
    try:
        parsed = parse_auth_header(auth_header)
        auth_dict = read_token(parsed.split(':')[1])
    except:
        return None

    try:
        user = Users.get(Users.name == auth_dict['user'],
                         Users.enabled == True)
    except:
        user = None
    return user
