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
        pass

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
