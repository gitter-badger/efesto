# -*- coding: utf-8 -*-
"""
    The models used by Efesto.
"""
import os
"""
from peewee import (PrimaryKeyField, CharField, IntegerField, DateTimeField,
                    BooleanField, ForeignKeyField)
                    """
from peewee import *
from playhouse.signals import Model, pre_save


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
    last_login = DateTimeField(null=True)

    def can(self, action, item):
        if self.rank == 10:
            return True
        else:
            model_name = getattr(item._meta, 'db_table')
            rules = AccessRules.select()\
            .where(
                (AccessRules.user == self.id) | (AccessRules.rank == self.rank),
                AccessRules.model == model_name,
                (AccessRules.item == None) | (AccessRules.item == item.id),
                getattr(AccessRules, action) != None
            )\
            .order_by(AccessRules.level.desc(), AccessRules.item.asc()).limit(1)
            if len(rules) > 0:
                if getattr(rules[0], action) == 1:
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
    model = CharField(null=True)
    level = IntegerField()
    read = IntegerField(null=True)
    edit = IntegerField(null=True)
    eliminate = IntegerField(null=True)


class EternalTokens(Base):
    """
    EternalTokens can be used to store server-side tokens that can need to be
    revoked when needed.
    """
    id = PrimaryKeyField(primary_key=True)
    name = CharField()
    user = ForeignKeyField(Users)
    token = CharField()


@pre_save(sender=EternalTokens)
def on_token_save(model_class, instance, created):
    """
    """
    dirty = getattr(instance, '_dirty')
    if 'token' in dirty:
        instance.token = hexlify_(os.urandom(24))


def make_model(custom_type):
    """
    Generates a model based on a Type entry, using the columns specified in
    Fields.
    """
    if custom_type.enabled == True:
        attributes = {}
        attributes['owner'] = ForeignKeyField(Users)
        fields_dict = {'string': CharField, 'int': IntegerField, 'bool':BooleanField, 'date': DateTimeField }
        columns = Fields.select().where( Fields.type==custom_type.id )
        for column in columns:
            attributes[column.name] = fields_dict[column.field_type]()
        model = type("%s" % (custom_type.name), (Base, ), attributes)
        db.create_tables([model], safe=True)
        return model
    else:
        raise ValueError("Cannot generate a model for a disabled type")
