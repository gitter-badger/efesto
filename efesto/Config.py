# -*- coding: utf-8 -*-
"""
    Configuration
"""
import configparser
import os


class Config(object):

    def __init__(self, config_file='efesto.cfg'):
        self.path = self.find_path(config_file)
        self.parser = configparser.ConfigParser()
        self.parser.read(self.path)

    def find_path(self, path):
        fullpath = os.path.join(os.getcwd(), path)
        if os.path.isfile(fullpath) == True:
            return fullpath
        raise ValueError('The configuration file was not found at %s' % (path))
