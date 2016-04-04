# -*- coding: utf-8 -*-
"""
    The models used by Efesto.
"""
from peewee import (PrimaryKeyField, CharField, IntegerField, DateTimeField,
                    BooleanField, ForeignKeyField)
from playhouse.signals import Model, pre_save


from .Base import db
from .Crypto import generate_hash


class Base(Model):
    """A base model that will use our Postgresql database"""
    class Meta:
        database = db


class Users(Base):
    """
    Users.
    """
    id = PrimaryKeyField(primary_key=True)
    name = CharField(unique=True)
    email = CharField()
    password = CharField()
    rank = IntegerField()
    last_login = DateTimeField(null=True)


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


class Fields(Base):
    """
    The fields are used to generate the columns for custom models/tables for
    the types specified in Types.
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
    type = ForeignKeyField(Types, null=True)
    level = IntegerField()
    read = IntegerField(null=True)
    edit = IntegerField(null=True)
    delete = IntegerField(null=True)


class EternalTokens(Base):
    """
    EternalTokens can be used to store server-side tokens that can need to be
    revoked when needed.
    """
    id = PrimaryKeyField(primary_key=True)
    name = CharField()
    user = ForeignKeyField(Users)
    token = CharField()


def make_model(custom_type):
    """
    Generates a model based on a Type entry, using the columns specified in
    Fields.
    """
    if custom_type.name in db.get_tables():
        raise ValueError("A model for this type has been already generated")

    if custom_type.enabled == True:
        attributes = {}
        attributes['owner'] = ForeignKeyField(Users)
        fields_dict = {'string': CharField, 'int': IntegerField, 'bool':BooleanField }
        columns = Fields.select().where( Fields.type==custom_type.id )
        for column in columns:
            attributes[column.name] = fields_dict[column.field_type]()
        model = type("%s" % (custom_type.name), (Base, ), attributes)
        db.create_tables([model], safe=True)
        return model
    else:
        raise ValueError("Cannot generate a model for a disabled type")
