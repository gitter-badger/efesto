# -*- coding: utf-8 -*-
"""
    Resources
"""
import falcon


from .Models import *


def make_resource(model):
    """
    Generates a resource class.
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
