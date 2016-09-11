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


def hinder(data, cls=None, path=None, page=None, last_page=None):
    siren = {}
    if type(data) == dict:
        siren['properties'] = data
        if path:
            current_path = '{}/{}'.format(path, data['id'])
            siren['links'] = [{'rel': ['self'], 'href': current_path}]
    elif type(data) == list:
        siren['properties'] = {'count': len(data)}
        if path:
            if page == None:
                siren['links'] = [{'rel': ['self'], 'href': path}]
            elif page > 0:
                current_path = '{}?page={}'.format(path, page)
                siren['links'] = [{'rel': ['self'], 'href': current_path}]
                if page > 1:
                    prev_path = '{}?page={}'.format(path, page - 1)
                    prev = {'rel': ['previous'], 'href': prev_path}
                    siren['links'].append(prev)
                if page != last_page:
                    next_path = '{}?page={}'.format(path, page + 1)
                    siren['links'].append({'rel': ['next'], 'href': next_path})

        entities = []
        for item in data:
            entity = {}
            entity['properties'] = item
        siren['entities'] = entities

    if cls:
        siren['class'] = [cls]
    return siren
