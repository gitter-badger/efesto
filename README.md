# Efesto
[![Pypi version](https://img.shields.io/pypi/v/efesto.svg?maxAge=3600&style=flat-square)](https://pypi.python.org/pypi/efesto)
[![Build status](https://img.shields.io/travis/Vesuvium/efesto.svg?maxAge=3600&style=flat-square)](https://travis-ci.org/Vesuvium/efesto)
[![Coverage](https://img.shields.io/codeclimate/coverage/github/Vesuvium/efesto.svg?maxAge=3600&style=flat-square)](https://codeclimate.com/github/Vesuvium/efesto)
[![Code Climate](https://img.shields.io/codeclimate/github/Vesuvium/efesto.svg?maxAge=3600&style=flat-square)](https://codeclimate.com/github/Vesuvium/efesto)

Efesto is a RESTful (micro)server that can be used for building an API in
minutes. It takes care of authentication, permissions and kickstarts you by
providing a simple way to build a data structure and the means to expose it.

Efesto follows the UNIX principle of doing one thing and well, leaving you the
freedom of choice about other components (e.g. caching, rate-limiting,
load balancer).

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

Then use efesto-quickstart:

```
vim efesto.cfg # edit the configuration to your needs
efesto-quickstart
```

Efesto is installed and set up; if you use gunicorn you can run it with:

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
Authorization: Basic anystring:someverylongtoken
# [ ... list of users ]
```
