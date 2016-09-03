# -*- coding: utf-8 -*-
"""
    The Config test case.

    Tests the Config module.
"""
import configparser
import os
import sys

from efesto.Config import Config
import pytest


sys.path.insert(0, '')


@pytest.fixture
def config():
    return Config()


def test_find_path(config, config_file):
    fullpath = config.find_path(config_file)
    assert fullpath == os.path.abspath(config_file)


def test_find_path_parent_folder(config):
    """
    Verifies that find_path is able to find the configuration file if it's
    in the working directory's parent folder.
    """
    path = '../test.cfg'
    f = open(path, 'w')
    f.close()
    fullpath = config.find_path('test.cfg')
    os.remove(path)
    assert os.path.abspath(fullpath) == os.path.abspath(path)


def test_find_path_exception(config):
    """
    Tests the find_path method behaviour when called with a non-existing path.
    """
    with pytest.raises(ValueError):
        config.find_path('somerandomname')


def test_config_has_path(config):
    """
    Tests whether the config has a path attribute.
    """
    assert hasattr(config, 'path')
    if hasattr(config, 'path'):
        assert getattr(config, 'path') == os.path.abspath('efesto.cfg')


def test_config_has_parser(config):
    """
    Tests whether the config has a parser attribute.
    """
    assert hasattr(config, 'parser')
    if hasattr(config, 'parser'):
        assert isinstance(getattr(config, 'parser'), configparser.ConfigParser)


@pytest.mark.parametrize('options', [
    ['main', 'installed'],
    ['db', 'name', 'user', 'password', 'host'],
    ['security', 'secret', 'token_expiration', 'salt_length', 'iterations',
     'key_length']
])
def test_default_config(config, options):
    """
    Tests for existance of default configuration
    """
    section = options.pop(0)
    for option in options:
        value = config.parser.get(section, option)
        assert value != None
