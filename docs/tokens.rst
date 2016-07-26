Tokens
======

In Efesto there two types of tokens: standard and eternal. When a client
authenticates, it uses either one.

Standard tokens
###############
Standard tokens are time-bound tokens stored on clients. Efesto does not force
a way to store these tokens on the client, rather is the client responsibility
whether and how to store them.

.. note::

    The expiration time of standard tokens can be set in the configuration


Eternal tokens
##############
Eternal tokens differ from standard tokens because, as you may guess, they do
not expire.
Efesto stores eternal tokens, so they can be revoked whenever they are not
needed anymore.
