Security
========
Security is an important part of an application, perharps the most important one!


Passwords
#########
Password are salted and encrypted using 
`PBKDF2 <https://en.wikipedia.org/wiki/PBKDF2>`_. If you want stronger password
encryption, you can change the values of security.salt_length, security.iterations, 
security.key_length in the configuration

Tokens
######
The standard tokens that are used in authentication are generated with
`itsdangerous <http://pythonhosted.org/itsdangerous/>`_.

If you want to increase the tokens security, you can change the values of
security.token_expiration and security.secret



