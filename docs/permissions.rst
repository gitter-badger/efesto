Permissions
###########
Efesto has a powerful permissions system that allows to set permissions on
items or types, targeting a single user or a group of users, for a specific
action (read, edit, delete).

.. note::
    Efesto manages permissions in strict way: by default, only admins can
    perform actions.

Permissions can also be stacked, in this case the level of the permission is
used to decide how important a permission is, when compared to others.

.. note::
    An user can never set a permission with a level higher than its own rank.
