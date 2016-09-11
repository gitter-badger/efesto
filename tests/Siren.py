# -*- coding: utf-8 -*-
"""
    The Efesto Siren tests suite.

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
from efesto.Siren import hinder
import pytest


@pytest.fixture
def siren_resource():
    return {'id': 1, 'name': 'Francis', 'surname': 'Drake'}


@pytest.fixture
def siren_collection(siren_resource):
    john = {'id': 2, 'name': 'John', 'surname': 'Hawkins'}
    jack = {'id': 3, 'name': 'Jack', 'surname': 'Sparrow'}
    return [siren_resource, john, jack]


def test_hinder_resource_properties(siren_resource):
    result = hinder(siren_resource)
    assert 'properties' in result
    for key in siren_resource:
        assert result['properties'][key] == siren_resource[key]


def test_hinder_resource_links(siren_resource):
    result = hinder(siren_resource, path='/captains')
    assert 'links' in result
    assert result['links'][0]['rel'] == ['self']
    assert result['links'][0]['href'] == '/captains'


def test_hinder_resource_class(siren_resource):
    result = hinder(siren_resource, cls='captain')
    assert 'class' in result
    assert result['class'] == ['captain']


def test_hinder_collection_properties(siren_collection):
    result = hinder(siren_collection)
    assert result['properties']['count'] == len(siren_collection)


def test_hinder_collection_pagination_hrefs(siren_collection):
    result = hinder(siren_collection, path='/captains', page=2)
    d = {}
    for i in result['links']:
        d[i['rel'][0]] = i['href']
    assert d['self'] == '/captains?page=2'
    assert d['next'] == '/captains?page=3'
    assert d['previous'] == '/captains?page=1'


def test_hinder_collection_pagination_rels(siren_collection):
    result = hinder(siren_collection, path='/captains', page=2)
    rels = [i['rel'] for i in result['links']]
    assert ['self'] in rels
    assert ['next'] in rels
    assert ['previous'] in rels


def test_hinder_collection_first_page(siren_collection):
    result = hinder(siren_collection, path='/captains', page=1)
    rels = [i['rel'] for i in result['links']]
    assert ['self'] in rels
    assert ['next'] in rels
    assert ['previous'] not in rels


def test_hinder_collection_last_page(siren_collection):
    result = hinder(siren_collection, path='/captains', page=3, last_page=3)
    rels = [i['rel'] for i in result['links']]
    assert ['self'] in rels
    assert ['previous'] in rels
    assert ['next'] not in rels


def test_hinder_collection_entities_properties(siren_collection):
    result = hinder(siren_collection)
    properties = siren_collection[0].keys()
    assert len(result['entities']) == len(siren_collection)
    for item in result['entities']:
        assert item['properties'].keys() == properties


def test_hinder_collection_entities_rel(siren_collection):
    result = hinder(siren_collection, path='/captains', page=3, last_page=3)
    for item in result['entities']:
        assert item['rel'] == ['item']


def test_hinder_collection_entities_href(siren_collection):
    result = hinder(siren_collection, path='/captains', page=3, last_page=3)
    for item in result['entities']:
        item_id = item['properties']['id']
        assert '/captains/' + str(item_id) in item['href']
