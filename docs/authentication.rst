Authentication
==============
In Efesto, you authenticate with a token and HTTP Basic Auth.

To get the token, make a POST request to the auth endpoint. If your
credentials are correct, the server will respond with a token that you can use
to authenticate your future requests::

    POST http://example.com/auth?username=myuser&password=mypasswd

Efesto will respond with::

    {'token': 'averylongandrandomtoken'}

Now you are authenticated, and can make requests to endpoints::

    Header HTTP Basic anystring:mytoken
    GET/POST/PATCH/DELETE http://example.com/{my_endpoint}
