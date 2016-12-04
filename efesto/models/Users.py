# -*- coding: utf-8 -*-
"""
    The Users model.

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
from peewee import BooleanField, CharField, DateTimeField, IntegerField, PrimaryKeyField
from efesto.Crypto import generate_hash
from playhouse.signals import pre_save


class Users(Base):
    """
    Users.
    """
    id = PrimaryKeyField(primary_key=True)
    name = CharField(unique=True)
    email = CharField()
    password = CharField()
    rank = IntegerField()
    enabled = BooleanField()
    last_login = DateTimeField(null=True)

    def can(self, requested_action, item):
        if self.rank == 10:
            return True
        else:
            if requested_action == 'create':
                action = 'read'
            else:
                action = requested_action
            model_name = getattr(item._meta, 'db_table')
            rules = AccessRules.select()\
                .where((AccessRules.user == self.id) |
                       (AccessRules.rank == self.rank))\
                .where(AccessRules.model == model_name)\
                .where((AccessRules.item == None) |
                       (AccessRules.item == item.id))\
                .where(getattr(AccessRules, action) != None)\
                .order_by(AccessRules.level.desc(), AccessRules.item.asc(),
                          AccessRules.rank.desc())\
                .limit(1)
            if len(rules) > 0:
                if requested_action == 'create':
                    if getattr(rules[0], action) >= 5:
                        return True
                    else:
                        return False
                else:
                    if getattr(rules[0], action) >= 1:
                        return True
                    else:
                        return False
            return False



@pre_save(sender=Users)
def on_user_save(model_class, instance, created):
    """
    Hashes the password.
    """
    dirty = getattr(instance, '_dirty')
    if 'password' in dirty:
        instance.password = generate_hash(instance.password)
