# -*- coding: utf-8 -*-
"""
    The Efesto Blueprints tests suite.

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
import os
import sys
from configparser import ConfigParser

from efesto.Blueprints import dump_blueprint, load_blueprint
from efesto.Models import Fields, Types
import pytest


sys.path.insert(0, '')


@pytest.fixture
def blueprint_file():
    return 'testblueprint.cfg'


@pytest.fixture
def simple_blueprint(request, blueprint_file):
    blueprint = """
    [flowers]
    fields = name, colour
    """
    with open(blueprint_file, 'w') as f:
        f.write(blueprint)

    def teardown():
        os.remove(blueprint_file)
        field = Fields.get(Fields.name == 'name')
        field.delete_instance()
        field = Fields.get(Fields.name == 'colour')
        field.delete_instance()
        type = Types.get(Types.name == 'flowers')
        type.delete_instance()
    request.addfinalizer(teardown)


@pytest.fixture
def complex_blueprint(request, blueprint_file):
    blueprint = """
    [colours]
    fields = name

    [plants]
    fields = name, colour, weight
    [plants.weight]
    type = int
    [plants.colour]
    type = colours
    """
    with open(blueprint_file, 'w') as f:
        f.write(blueprint)

    def teardown():
        os.remove(blueprint_file)
        field = Fields.get(Fields.name == 'name')
        field.delete_instance()
        field = Fields.get(Fields.name == 'name')
        field.delete_instance()
        field = Fields.get(Fields.name == 'weight')
        field.delete_instance()
        field = Fields.get(Fields.name == 'colour')
        field.delete_instance()
        type = Types.get(Types.name == 'colours')
        type.delete_instance()
        type = Types.get(Types.name == 'plants')
        type.delete_instance()
    request.addfinalizer(teardown)


@pytest.fixture
def simple_data(request, blueprint_file):
    bands = Types(name='bands', enabled=0)
    bands.save()
    name = Fields(name='band_name', type=bands.id, field_type='string')
    name.save()

    def teardown():
        name.delete_instance()
        bands.delete_instance()
        os.remove(blueprint_file)
    request.addfinalizer(teardown)


@pytest.fixture
def complex_data(request, blueprint_file):
    ships = Types(name='ships', enabled=0)
    ships.save()
    tonnage = Fields(name='tonnage', type=ships.id, field_type='int')
    tonnage.save()
    flag = Fields(name='flag', type=ships.id, field_type='string')
    flag.save()

    def teardown():
        tonnage.delete_instance()
        flag.delete_instance()
        ships.delete_instance()
        os.remove(blueprint_file)
    request.addfinalizer(teardown)


def test_load_simple_blueprint(simple_blueprint, blueprint_file):
    """
    Tests the loading of a simple blueprint that has only a list of fields.
    """
    load_blueprint(blueprint_file)
    type = Types.get(Types.name == 'flowers')
    assert type.id > 0
    assert type.enabled == True
    fields = ['name', 'colour']
    for field_name in fields:
        field = Fields.get(Fields.name == field_name)
        assert field.field_type == 'string'
        assert field.type.id == type.id


def test_complex_blueprint(complex_blueprint, blueprint_file):
    """
    Tests the loading of blueprint with fields description.
    """
    load_blueprint(blueprint_file)
    type = Types.get(Types.name == 'plants')
    assert type.id > 0

    field = Fields.get(Fields.name == 'weight')
    assert field.field_type == 'int'
    assert field.type.id == type.id

    field = Fields.get(Fields.name == 'colour')
    assert field.field_type == 'colours'
    assert field.type.id == type.id


def test_dump_simple_blueprint(simple_data, blueprint_file):
    """
    Tests the dumping of a simple blueprint.
    """
    dump_blueprint(blueprint_file)
    parser = ConfigParser()
    parser.read(blueprint_file)
    assert parser.sections() == ['bands']
    assert parser.get('bands', 'fields') == 'band_name'


def test_dump_complex_blueprint(complex_data, blueprint_file):
    """
    Tests the dumping of a complex blueprint.
    """
    dump_blueprint(blueprint_file)
    parser = ConfigParser()
    parser.read(blueprint_file)
    assert parser.sections() == ['ships', 'ships.tonnage']
    assert parser.get('ships.tonnage', 'type') is not None

    fields = parser.get('ships', 'fields').split(',')
    assert 'tonnage' in fields or ' tonnage' in fields
    assert 'flag' in fields or ' flag' in fields
