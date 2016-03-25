# -*- coding: utf-8 -*-
"""
    Resources
"""
import falcon


from .Models import *


def make_resource(model):
    """
    The make_resource function acts as generator of resources for models.
    """
    def on_get(self, request, response):
        if request.auth:
            pass
        else:
            raise falcon.HTTPUnauthorized('Login required', 'You need to login', scheme='Basic realm="Login Required"')

    def on_post():
        pass

    def on_delete():
        pass

    def on_patch():
        pass

    attributes = {
        'on_get': on_get,
        'on_post': on_post,
        'on_patch': on_patch,
        'on_delete': on_delete
    }
    return type('myresource', (object, ), attributes)


class TokensResource:
    """
    The TokensResource resource handles tokens requests.
    """
    def on_post(self, request, response):
        if not 'password' in request.params or not 'username' in request.params:
            raise falcon.HTTPBadRequest('', '')

        try:
            user = Users.get(Users.name == request.params['username'])
        except:
            user = None

        if user == None:
            raise falcon.HTTPUnauthorized('Login required', 'You need to login', scheme='Basic realm="Login Required"')

        response.status = falcon.HTTP_OK
        response.body = '{"token":"mytoken"}'
