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


def parse_section(parser, field_section, field_dict):
    """
    Parses a blueprint field section.
    """
    options = parser.options(field_section)
    if 'type' in options:
        field_dict['field_type'] = parser.get(field_section, 'type')
    if 'nullable' in options:
        field_dict['nullable'] = parser.getboolean(field_section, 'nullable')


def write_field(type, field, parser):
    """
    Writes a field in the blueprint file, if it has any field that differs
    from the default values expected for a field.
    """
    special_values = {}
    if field.field_type != 'string':
        special_values['type'] = field.field_type
    if field.nullable == False:
        special_values['nullable'] = field.nullable

    if len(special_values) > 0:
        field_section = '{}.{}'.format(type.name, field.name)
        parser.add_section(field_section)

        for key in special_values:
            value = special_values[key]
            parser.set(field_section, key, str(value))
        parser.set(field_section, 'type', field.field_type)


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
            field_dict = {'name': field.strip(), 'type': new_type.id}
            field_dict['field_type'] = 'string'
            field_dict['nullable'] = True
            field_section = '{}.{}'.format(type, field_dict['name'])
            if parser.has_section(field_section):
                parse_section(parser, field_section, field_dict)
            new_field = Fields(**field_dict)
            new_field.save()
        new_type.enabled = 1
        new_type.save()


def dump_blueprint(blueprint_file):
    """
    Dumps a blueprint, creating a blueprint file from the database data.
    """
    parser = ConfigParser()
    types = Types.select()
    for type in types:
        parser.add_section(type.name)
        fields = Fields.select().where(Fields.type == type.id)
        fields_list = []
        for field in fields:
            write_field(type, field, parser)
            fields_list.append(field.name)
        parser.set(type.name, 'fields', ', '.join(fields_list))

    with open(blueprint_file, 'w') as blueprint:
        parser.write(blueprint)
