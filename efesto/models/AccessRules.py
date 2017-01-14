# -*- coding: utf-8 -*-
"""
    The AccessRules model.

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
from .Base import Base
from .Users import Users
from peewee import CharField, ForeignKeyField, IntegerField, PrimaryKeyField


class AccessRules(Base):
    """
    AccessRules define the permissions that an users or a group of users have
    on a single item or on a group of items.
    """
    id = PrimaryKeyField(primary_key=True)
    item_id  = IntegerField()
    item_type = CharField()
    user_permission = IntegerField()
    group = IntegerField()
    group_permission = IntegerField()
    others_permission = IntegerField()
    user_id = ForeignKeyField(Users)
