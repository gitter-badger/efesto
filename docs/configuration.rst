Configuration
=============
Efesto configuration resides in a file called 'efesto.cfg'. The configuration
file can be in your working directory or in its parent folder.

Options
#######

main.installed
--------------
Whether Efesto is installed.

db.host
-------
The database hostname.

db.name
-------
The database name.

db.user
-------
The database user.

db.password
-----------
The database password.

security.secret
---------------
The secret. This is a random string that is used for encryption. The quickstart
script will automatically generate one.

security.token_expiration
-------------------------
The expiration time in seconds of a standard token. The default value is 3600.

security.salt_length
--------------------
The length of the salt used in passwords in bytes. The default value is 8.

security.iterations
-------------------
The number of encryption rounds to perform when encrypting passwords. The
default value is 1000.

security.key_length
-------------------
The length of the password's encrypted key. The default value is 24.
