# -*- coding: utf-8 -*-
"""
    The Efesto Siren module.

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


def make_entities(data, path=None):
    entities = []
    for item in data:
        entity = {}
        new = {}
        subentities = []
        for i in item:
            if type(item[i]) is not dict:
                new[i] = item[i]
            else:
                subentities.append(item[i])
        entity['properties'] = new
        if len(subentities) > 0:
            entity['entities'] = make_entities(subentities)
        if path:
            href = '{}/{}'.format(path, item['id'])
            entity['href'] = href
        entity['rel'] = ['item']
        entities.append(entity)
    return entities


def hinder(data, cls=None, path=None, page=None, last_page=None):
    siren = {}
    if type(data) == dict:
        siren['properties'] = data
        if path:
            siren['links'] = [{'rel': ['self'], 'href': path}]
    elif type(data) == list:
        siren['properties'] = {'count': len(data)}
        if path:
            if page == None:
                siren['links'] = [{'rel': ['self'], 'href': path}]
            elif page > 0:
                current_path = '{}?page={}'.format(path, page)
                if page == 1:
                    current_path = path
                siren['links'] = [{'rel': ['self'], 'href': current_path}]
                if page > 1:
                    prev_path = '{}?page={}'.format(path, page - 1)
                    prev = {'rel': ['previous'], 'href': prev_path}
                    siren['links'].append(prev)
                if last_page:
                    last_path = '{}?page={}'.format(path, last_page)
                    siren['links'].append({'rel': ['last'], 'href': last_path})
                    if last_page > page:
                        next_path = '{}?page={}'.format(path, page + 1)
                        next = {'rel': ['next'], 'href': next_path}
                        siren['links'].append(next)
                else:
                    next_path = '{}?page={}'.format(path, page + 1)
                    siren['links'].append({'rel': ['next'], 'href': next_path})

        siren['entities'] = make_entities(data, path)

    if cls:
        siren['class'] = [cls]
    return siren
