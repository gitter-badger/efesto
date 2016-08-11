# -*- coding: utf-8 -*-
"""
    Efesto travis script.

    This script sets up Efesto for travis, creating tables and settings.
"""
import sys

from efesto.Base import config


sys.path.insert(0, '')


config.parser.set('db', 'name', 'test')
config.parser.set('db', 'user', 'postgres')
config.parser.set('db', 'password', '')
with open(config.path, 'w') as configfile:
    config.parser.write(configfile)
