# Efesto
Efesto is a RESTful API generator based on the Falcon framework. It allows you
to build and deploy awesome relational APIs in minutes.


## Features

* Custom data types
* Client-side and server-side tokens
* A powerful and simple permissions system
* PostgreSQL based

## Installing

Efesto currently supports only Python3. You will also need to install and
configure PostgreSQL, and a server like uwsgi or gunicorn.

```
pip3 install efesto
```

Create the configuration for efesto. Have a look at the provided efesto.cfg
for an example.
At the very minimum you will need to edit the db details (host, db, user,
password).

Then run the install.py script found in scripts/install.py (you will need to
copy this from the repo).

```
touch efesto.cfg
# edit to your needs
nano efesto.cfg
python3 scripts/install.py
```

Efesto is installed; if you use gunicorn you can run it with:

```
gunicorn efesto:app
```

## Making actual requests

Efesto only allows authenticated users to make requests. By default, all users
have no permissions, except for the administrators.

Use the /auth endpoint to get a authentication token.
Note that this is a timed token that will expire after some time. If you want
a non-expiring token, use an eternal token.

```
POST http://myhost.com/auth
username=myuser&password=mypasswd

# {'token':'someverylongtoken'}
```

Then, use the token to authenticate with HTTP Basic, sending the token as
username.

```
GET http://myhost.com/users
Authorization: Basic someverylongtoken:
# [ ... list of users ]
```
