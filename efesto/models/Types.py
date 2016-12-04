# -*- coding: utf-8 -*-
"""
    The Types model.

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
from peewee import BooleanField, CharField, PrimaryKeyField
from playhouse.signals import post_delete, pre_delete


class Types(Base):
    """
    The Types specify the custom types that should be generated. Only enabled
    types will be generated.
    """
    id = PrimaryKeyField(primary_key=True)
    name = CharField(unique=True)
    enabled = BooleanField()

    def make_model(custom_type):
        """
        Generates a model based on a Type entry, using the columns specified in
        Fields.
        """
        if custom_type.enabled:
            attributes = {}
            attributes['owner'] = ForeignKeyField(Users)
            columns = Fields.select().where(Fields.type == custom_type.id)
            for column in columns:
                attributes[column.name] = make_field(custom_type, column)
            model = type('%s' % (custom_type.name), (Base, ), attributes)
            db.create_tables([model], safe=True)
            return model
        raise ValueError('Cannot generate a model for a disabled type')


@post_delete(sender=Types)
def on_type_delete(model_class, instance):
    """
    Drops a type table when the type is deleted.
    """
    model = make_model(instance)
    model.drop_table()


@pre_delete(sender=Types)
def on_type_pre_delete(model_class, instance):
    """
    Checks whether a type has existing instances.
    """
    instance.enabled = 1
    instance.save()
    model = make_model(instance)
    if model.select().count() > 0:
        raise ValueError('This type has still existing instances')
