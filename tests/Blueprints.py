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
from efesto.models import Fields, Types
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
    fields = name, colour, weight, age
    [plants.weight]
    type = int
    [plants.age]
    type = date
    [plants.colour]
    type = colours
    """
    with open(blueprint_file, 'w') as f:
        f.write(blueprint)
        f.close()

    def teardown():
        os.remove(blueprint_file)
        field = Fields.get(Fields.name == 'name')
        field.delete_instance()
        field = Fields.get(Fields.name == 'name')
        field.delete_instance()
        field = Fields.get(Fields.name == 'weight')
        field.delete_instance()
        field = Fields.get(Fields.name == 'age')
        field.delete_instance()
        field = Fields.get(Fields.name == 'colour')
        field.delete_instance()
        type = Types.get(Types.name == 'colours')
        type.delete_instance()
        type = Types.get(Types.name == 'plants')
        type.delete_instance()
    request.addfinalizer(teardown)


@pytest.fixture
def nullable_blueprint(request, complex_blueprint, blueprint_file):
    parser = ConfigParser()
    parser.read(blueprint_file)
    parser.add_section('plants.children')
    parser.set('plants.children', 'nullable', 'True')
    fields = parser.get('plants', 'fields').split(',')
    fields.append(' children')
    parser.set('plants', 'fields', ','.join(fields))
    with open(blueprint_file, 'w') as f:
        parser.write(f)

    def teardown():
        field = Fields.get(Fields.name == 'children')
        field.delete_instance()
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
    builders = Types(name='builders', enabled=0)
    builders.save()
    ships = Types(name='ships', enabled=0)
    ships.save()
    tonnage = Fields(name='tonnage', type=ships.id, field_type='int')
    tonnage.save()
    flag = Fields(name='flag', type=ships.id, field_type='string')
    flag.save()
    launch_date = Fields(name='launch_date', type=ships.id, field_type='date')
    launch_date.save()
    builder = Fields(name='builder', type=ships.id, field_type='builders')
    builder.save()

    def teardown():
        tonnage.delete_instance()
        flag.delete_instance()
        launch_date.delete_instance()
        builder.delete_instance()
        ships.delete_instance()
        builders.delete_instance()
        os.remove(blueprint_file)
    request.addfinalizer(teardown)


@pytest.fixture
def nullable_field(request, complex_data):
    ships = Types.get(Types.name == 'ships')
    sails = Fields(name='sails', type=ships.id, field_type='string',
                   nullable=False)
    sails.save()

    def teardown():
        sails.delete_instance()
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
        assert field.nullable == True


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

    field = Fields.get(Fields.name == 'age')
    assert field.field_type == 'date'
    assert field.type.id == type.id

    field = Fields.get(Fields.name == 'colour')
    assert field.field_type == 'colours'
    assert field.type.id == type.id


def test_nullable_blueprint(nullable_blueprint, blueprint_file):
    load_blueprint(blueprint_file)
    field = Fields.get(Fields.name == 'children')
    assert field.nullable == True


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
    expected_sections = ['ships', 'ships.tonnage', 'ships.launch_date',
                         'builders']
    for expected in expected_sections:
        assert expected in parser.sections()
    assert parser.get('ships.tonnage', 'type') is not None
    assert parser.get('ships.launch_date', 'type') == 'date'
    assert parser.get('ships.builder', 'type') == 'builders'

    fields = parser.get('ships', 'fields').split(',')
    assert 'tonnage' in fields or ' tonnage' in fields
    assert 'flag' in fields or ' flag' in fields
    assert 'launch_date' in fields or ' launch_date' in fields


def test_dump_nullable_field(nullable_field, blueprint_file):
    """
    Tests whether dump_blueprint can handle nullable fields.
    """
    dump_blueprint(blueprint_file)
    parser = ConfigParser()
    parser.read(blueprint_file)
    assert 'ships.sails' in parser.sections()
    assert parser.getboolean('ships.sails', 'nullable') == False
