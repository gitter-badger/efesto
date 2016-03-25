# -*- coding: utf-8 -*-
"""
    The models used by Efesto.
"""
from peewee import *


from .Base import db


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


class Types(Base):
    """
    The Types specify the custom types that should be generated. Only enabled
    types will be generated.
    """
    id = PrimaryKeyField(primary_key=True)
    name = CharField()
    enabled = BooleanField()


class Fields(Base):
    """
    The fields are used to generate the columns for custom models/tables for
    the types specified in Types.
    """
    id = PrimaryKeyField(primary_key=True)
    name = CharField()
    type = ForeignKeyField(Types)
    foreign = CharField()
    unique = BooleanField()
    label = CharField()
    description = CharField()


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
