# -*- coding: utf-8 -*-
"""
    Efesto quickstart script.

    This script will set up Efesto, creating the tables, the secret and the
    administrator account.
"""
import argparse
import getpass
import os
import sys
from binascii import hexlify

from colorama import Fore, Style
import efesto
from efesto.Base import config, db
from efesto.Models import AccessRules, EternalTokens, Fields, Types, Users
from peewee import OperationalError, ProgrammingError


sys.path.insert(0, '')


def message(message, colour):
    """
    Prints a coloured message using colorama.
    """
    text_colours = {'green': Fore.GREEN, 'red': Fore.RED, 'blue': Fore.BLUE}
    print(text_colours[colour] + message + Style.RESET_ALL)


def create_tables():
    """
    Creates the tables.
    """
    try:
        db.create_tables([Users, Types, Fields, AccessRules, EternalTokens])
        message('Tables created!', 'green')
    except OperationalError:
        message(('An error occured during tables creation. '
                 'Please check your database credentials.'), 'red')
        exit()
    except ProgrammingError:
        message(('An error occurred during tables creation. '
                 'Please check your database.'), 'red')
        exit()
    except:
        message('An unknown error occurred during tables creation', 'red')
        exit()


def create_config():
    secret_key = str(hexlify(os.urandom(24)), encoding='utf8')
    config.parser.set('main', 'installed', 'True')
    config.parser.set('security', 'secret', secret_key)
    with open(config.path, 'w') as configfile:
        config.parser.write(configfile)
        message('Configuration successfully updated!', 'green')


def create_admin():
    """
    Creates the default administrator.
    """
    print('Efesto will now create the default administrator')
    admin_name = input('Administrator name: ')
    admin_email = input('Administrator email: ')
    admin_password = getpass.getpass('Administrator password: ')
    admin = Users(name=admin_name, email=admin_email, rank=10,
                  password=admin_password, enabled=True)
    admin.save()
    print(Fore.GREEN + 'Admin created!')


def quickstart():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-admin', dest='admin', action='store_false')
    parser.set_defaults(admin=True)
    args = parser.parse_args()
    installed = config.parser.getboolean('main', 'installed')
    if installed != True:
        message('This script will help you setup Efesto', 'blue')
        version_message = 'Efesto version: %s' % (efesto.__version__)
        message(version_message, 'blue')
        create_tables()
        create_config()
        if args.admin:
            create_admin()
        message('Set up successful.', 'green')
    else:
        message('It seems Efesto has been already set up!', 'red')


if __name__ == '__main__':
    quickstart()
