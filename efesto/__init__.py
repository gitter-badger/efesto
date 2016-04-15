# -*- coding: utf-8 -*-
"""
    Efesto
"""
import falcon


from .Resources import make_collection, make_resource, TokensResource
from .Models import (Users, Types, Fields, AccessRules, EternalTokens)


app = falcon.API()
for i in [['/users', Users], ['/types', Types], ['/fields', Fields],
        ['/rules', AccessRules], ['/tokens', EternalTokens]]:
    collection = make_collection(i[1])()
    resource = make_resource(i[1])()
    app.add_route(i[0], collection)
    app.add_route("%s/{id}" % i[0], resource)

app.add_route("/auth", TokensResource())


def error_serializer(req, exception):
    preferred = 'application/json'
    representation = exception.to_json()
    return (preferred, representation)
app.set_error_serializer(error_serializer)
