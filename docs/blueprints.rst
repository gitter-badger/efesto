Blueprints
==========
Blueprints are a quick way to create, load and save custom types and their 
fields. It is also a clearer way of creating a data structure because they give
a clearer view of what is going on, compared to API calls or SQL statements.

A blueprint is an ini-like file that uses the Python
`configparser <https://docs.python.org/3/library/configparser.html>`_ syntax.

.. note::
    A blueprint file can have any name
    
    
Creating a blueprint
####################
Use configparser sections to mark types and the *fields* key to mark the 
fields for that type.

Loading a blueprint
###################
To load a blueprint use::

    efesto-blueprints --load myblueprint.cfg
    
Dumping a blueprint
###################
To dump a blueprint use::
    
    efesto-blueprints --dump mydump.cfg




