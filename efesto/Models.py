# -*- coding: utf-8 -*-
"""
    The models used by Efesto.

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
from peewee import (BooleanField, CharField, DateTimeField, FloatField,
                    ForeignKeyField, IntegerField, PrimaryKeyField, TextField)
from playhouse.signals import Model, post_delete, pre_delete, pre_save


from .Base import db
from .Crypto import generate_hash, hexlify_


class Base(Model):
    """A base model that will use our Postgresql database"""
    class Meta:
        database = db
        validate_backrefs = False


class Users(Base):
    """
    Users.
    """
    id = PrimaryKeyField(primary_key=True)
    name = CharField(unique=True)
    email = CharField()
    password = CharField()
    rank = IntegerField()
    enabled = BooleanField()
    last_login = DateTimeField(null=True)

    def can(self, requested_action, item):
        if self.rank == 10:
            return True
        else:
            if requested_action == 'create':
                action = 'read'
            else:
                action = requested_action
            model_name = getattr(item._meta, 'db_table')
            rules = AccessRules.select()\
                .where((AccessRules.user == self.id) |
                       (AccessRules.rank == self.rank))\
                .where(AccessRules.model == model_name)\
                .where((AccessRules.item == None) |
                       (AccessRules.item == item.id))\
                .where(getattr(AccessRules, action) != None)\
                .order_by(AccessRules.level.desc(), AccessRules.item.asc(),
                          AccessRules.rank.desc())\
                .limit(1)
            if len(rules) > 0:
                if requested_action == 'create':
                    if getattr(rules[0], action) >= 5:
                        return True
                    else:
                        return False
                else:
                    if getattr(rules[0], action) >= 1:
                        return True
                    else:
                        return False
            return False


@pre_save(sender=Users)
def on_user_save(model_class, instance, created):
    """
    Hashes the password.
    """
    dirty = getattr(instance, '_dirty')
    if 'password' in dirty:
        instance.password = generate_hash(instance.password)


class Types(Base):
    """
    The Types specify the custom types that should be generated. Only enabled
    types will be generated.
    """
    id = PrimaryKeyField(primary_key=True)
    name = CharField(unique=True)
    enabled = BooleanField()


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


class AccessRules(Base):
    """
    AccessRules define the permissions that an users or a group of users have
    on a single item or on a group of items.
    """
    id = PrimaryKeyField(primary_key=True)
    user = ForeignKeyField(Users, null=True)
    rank = IntegerField(null=True)
    item = IntegerField(null=True)
    model = CharField(null=True)
    level = IntegerField()
    read = IntegerField(null=True)
    edit = IntegerField(null=True)
    eliminate = IntegerField(null=True)


class EternalTokens(Base):
    """
    EternalTokens are server-stored tokens used for authentication purposes.
    Normally, Efesto would use client-stored tokens, but in some cases
    server-stored tokens are necessary.
    For example an application interacting with Efesto without requiring a
    final user's credentials (public data, password recovery, etc.)
    """
    id = PrimaryKeyField(primary_key=True)
    name = CharField()
    user = ForeignKeyField(Users)
    token = CharField()


@pre_save(sender=EternalTokens)
def on_token_save(model_class, instance, created):
    """
    Peewee hook that generates a random token whenever an eternal token is
    created.
    """
    dirty = getattr(instance, '_dirty')
    if 'token' in dirty:
        instance.token = hexlify_(os.urandom(24))


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
