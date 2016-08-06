# -*- coding: utf-8 -*-
"""
    The Efesto configuration module

    Copyright (C) 2016 Jacopo Cascioli

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import configparser
import os


class Config(object):

    def __init__(self, config_file='efesto.cfg'):
        self.path = self.find_path(config_file)
        self.parser = configparser.ConfigParser()
        self.parser.read(self.path)

    def find_path(self, path):
        """
        Finds the absolute path of the configuration file, looking in the
        current working directory (default) and its parent folder.

        The parent folder support is necessary for Sphinx.
        """
        possible_paths = [
            os.path.join(os.getcwd(), path),
            os.path.join(os.getcwd(), '..', path)
        ]
        for fullpath in possible_paths:
            if os.path.isfile(fullpath):
                return fullpath
        raise ValueError('The configuration file was not found at %s' % (path))
