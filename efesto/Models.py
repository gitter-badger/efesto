# -*- coding: utf-8 -*-
"""
    The models used by Efesto.
"""
from peewee import *


db = PostgresqlDatabase(
    'test',
    user='postgres',
    password='postgres',
    host='localhost'
)


class Base(Model):
    """A base model that will use our Postgresql database"""
    class Meta:
        database = db


class Users(Base):
    id = IntegerField(primary_key=True)
    name = CharField()
    email = CharField()
    password = CharField()
    rank = IntegerField()
    last_login = DateTimeField()


class Types(Base):
    id = IntegerField(primary_key=True)
    name = CharField()
    enabled = BooleanField()


class Fields(Base):
    id = IntegerField(primary_key=True)
    name = CharField()
    type = ForeignKeyField(Types)
    foreign = CharField()
    unique = BooleanField()
    label = CharField()
    description = CharField()


class AccessRules(Base):
    id = IntegerField(primary_key=True)
    user = ForeignKeyField(Users, null=True)
    rank = IntegerField(null=True)
    item = IntegerField(null=True)
    type = ForeignKeyField(Types, null=True)
    level = IntegerField()
    read = IntegerField(null=True)
    edit = IntegerField(null=True)
    delete = IntegerField(null=True)
