# -*- coding: utf-8 -*-
"""
    The Base module.
"""
from peewee import PostgresqlDatabase


from .Config import Config

config = Config()


db = PostgresqlDatabase(
    config.parser.get('db', 'name'),
    user=config.parser.get('db', 'user'),
    password=config.parser.get('db', 'password'),
    host=config.parser.get('db', 'host')
)
