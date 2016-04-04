# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "")


from efesto.Base import db, config
from efesto.Models import Users, Types, Fields, AccessRules, EternalTokens


if config.parser.getboolean('main', 'installed') != True:
    db.create_tables([Users, Types, Fields, AccessRules, EternalTokens])
    config.parser.set('main', 'installed', 'True')
    #config.parser.write(config.path)
