# -*- coding: utf-8 -*-
"""
   The Root resource.

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
import json


class RootResource:
    """
    The RootResource resource handles requests made to the root endpoint.
    """
    def __init__(self, data):
        self.data = data

    def on_get(self, request, response):
        response.body = json.dumps(self.data)
