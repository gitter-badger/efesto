# -*- coding: utf-8 -*-
"""
    The Fields model.

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
from .Base import Base
from .Types import Types
from peewee import BooleanField, CharField, ForeignKeyField, PrimaryKeyField


class Fields(Base):
    """
    The fields are used to generate the columns for custom models/tables for
    the types specified in Types.

    name: the name of the field
    type: the type to which the field belongs
    unique: whether the generated column should be unique
    nullable: whether the generated column should have be nullable
    label: a label for the column, for informative purposes
    description: a description for the column, for infformative purposes
    """
    id = PrimaryKeyField(primary_key=True)
    name = CharField()
    type = ForeignKeyField(Types)
    field_type = CharField()
    unique = BooleanField(null=True)
    nullable = BooleanField(null=True)
    label = CharField(null=True)
    description = CharField(null=True)

    def make_field(type, column):
        """
        Builds a field instance from a column.
        """
        default_fields = {'string': TextField, 'int': IntegerField,
                          'float': FloatField, 'bool': BooleanField,
                          'date': DateTimeField}
        if column.field_type in default_fields:
            args_dict = {}
            if column.nullable:
                args_dict['null'] = True
            if column.unique:
                args_dict['unique'] = True
            return default_fields[column.field_type](**args_dict)
        parent_type = Types.get(Types.name == column.field_type)
        if parent_type.id != type.id:
            parent_model = make_model(parent_type)
            return ForeignKeyField(parent_model)
        return ForeignKeyField('self', null=True)
