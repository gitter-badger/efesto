# -*- coding: utf-8 -*-
"""
    Efesto installation script.

    This script install Efesto, creating the tables, the secret and the
    administrator account.
"""
import sys
sys.path.insert(0, "")
import os
from binascii import hexlify
import getpass


from efesto.Base import db, config
from efesto.Models import Users, Types, Fields, AccessRules, EternalTokens


print('This script will install Efesto for you. ')
admin_name = input('Administrator name: ')
admin_email = input('Administrator email: ')
admin_password = getpass.getpass('Administrator password: ')
secret_key = str(hexlify(os.urandom(24)), encoding="utf8")


if config.parser.getboolean('main', 'installed') != True:
    config.parser.set('main', 'installed', 'True')
    config.parser.set('security', 'secret', secret_key)
    with open(config.path, 'w') as configfile:
        config.parser.write(configfile)

    db.create_tables([Users, Types, Fields, AccessRules, EternalTokens])
    admin = Users(name=admin_name, email=admin_email, rank=10, password=admin_password)
    admin.save()
