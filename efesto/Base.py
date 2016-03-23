# -*- coding: utf-8 -*-
"""
    The Base used for database connection.
"""
from peewee import PostgresqlDatabase


db = PostgresqlDatabase(
    'test',
    user='postgres',
    password='postgres',
    host='localhost'
)
