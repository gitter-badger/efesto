Tokens
======

Efesto uses tokens to authenticate clients. There are two types of tokens:
standard tokens, that expire after a certain amount of time, and eternal tokens,
that do not expire but can be revoked.

Standard tokens
###############
Standard tokens are emitted when a client authenticates successfully. Efesto
does not store them, rather is the client that stores the token and sends it
when making a request.

After a certain amount of time, a standard token will expire and it won't be
accepted by Efesto.

.. note::

    The expiration time of standard tokens can be set in the configuration


Eternal tokens
##############
Eternal tokens differ from standard tokens because, as you may guess, they do
not expire.
Efesto stores eternal tokens, so they can be revoked whenever they are not
needed anymore.
