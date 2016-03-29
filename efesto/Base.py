# -*- coding: utf-8 -*-
"""
    The Base module.
"""
from peewee import PostgresqlDatabase


from .Config import Config

config = Config()


db = PostgresqlDatabase(
    'test',
    user='postgres',
    password='postgres',
    host='localhost'
)
