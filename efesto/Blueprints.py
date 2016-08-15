# -*- coding: utf-8 -*-
"""
    The Efesto Blueprints module.

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
import os
from configparser import ConfigParser

from .Models import Fields, Types


def load_blueprint(blueprint):
    """
    Loads a blueprint in to the database from a blueprint file.
    """
    path = os.path.join(os.getcwd(), blueprint)
    parser = ConfigParser()
    parser.read(path)

    types = []
    for section in parser.sections():
        if '.' not in section:
            types.append(section)

    for type in types:
        new_type = Types(name=type, enabled=0)
        new_type.save()
        fields = parser.get(type, 'fields').split(',')
        for field in fields:
            field_name = field.strip()
            try:
                field_section = '{}.{}'.format(type, field_name)
                field_type = parser.get(field_section, 'type')
            except:
                field_type = 'string'
            new_field = Fields(name=field_name, type=new_type.id,
                               field_type=field_type)
            new_field.save()
        new_type.enabled = 1
        new_type.save()
