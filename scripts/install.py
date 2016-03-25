# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "")


from efesto.Config import Config
from efesto.Base import db
from efesto.Models import Users, Types, Fields, AccessRules


config = Config()
if config.parser.getboolean('main', 'installed') != True:
    db.create_tables([Users, Types, Fields, AccessRules])
    config.parser.set('main', 'installed', 'True')
    #config.parser.write(config.path)
