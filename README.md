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

## When do I use this?

* You need a full-fledged ReST API
* You are fine using Siren as hypermedia specification
* You need authentication and permissions but want the work already done
* You are fine with using PostgreSQL
* You want to be able to create models without writing code (Python or SQL)
* You need to easily import and export the models you created
* You have Python3.4+ on your production server :)


## Installing

You will need to install and configure PostgreSQL, and a server like uwsgi or
gunicorn.

```
pip3 install efesto
```

Configure Efesto, editing the configuration file. At the very minimum you
will need to provide the database details.

```
vim efesto.cfg
```

Use efesto-quickstart to have tables and admin created:

```
efesto-quickstart
```

Done! Now you can run your server and launch Efesto:

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
