# -*- coding: utf-8 -*-
"""
"""
import getpass
import os
import sys

import efesto
from efesto.Base import config
from efesto.Models import Users
from efesto.scripts.quickstart import create_admin, create_config, message
from efesto.scripts.travis import create_travis_config
import pytest


sys.path.insert(0, '')


@pytest.fixture
def input_mock(request):
    efesto.scripts.quickstart.input = lambda x: 'quickstart_admin'


@pytest.fixture
def getpass_mock(request):
    getpass.getpass = lambda x: 'passwd'


@pytest.mark.parametrize('colour', ['green', 'red', 'blue'])
def test_message(colour, capsys):
    text = 'some random message'
    message(text, colour)
    output, error = capsys.readouterr()
    assert text in output
    assert len(text) < len(output)


def test_create_config(config_file):
    config.path = os.path.join(os.getcwd(), config_file)
    create_config()
    assert config.parser.getboolean('main', 'installed') == True
    assert config.parser.get('security', 'secret') != None


def test_create_admin(input_mock, getpass_mock):
    create_admin()
    user = Users.get(Users.name == 'quickstart_admin')
    assert user.id != None
    user.delete_instance()


def test_create_travis_config(config_file):
    config.path = os.path.join(os.getcwd(), config_file)
    create_travis_config()
    assert config.parser.get('db', 'name') == 'test'
    assert config.parser.get('db', 'user') == 'postgres'
    assert config.parser.get('db', 'password') == ''
