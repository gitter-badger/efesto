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
