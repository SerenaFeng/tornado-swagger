#!/usr/bin/python
# -*- coding: utf-8 -*-
from tornado.web import URLSpec, StaticFileHandler

from tornado_swagger.settings import *
from tornado_swagger.views import *

__author__ = 'serena'

def swagger_handlers(prefix, **opts):
    if prefix[-1] != '/':
        prefix += '/'

    default_settings.update(opts)
    return [
        URLSpec(prefix + r'spec.html$',         SwaggerUIHandler,        default_settings, name=URL_SWAGGER_API_DOCS),
        URLSpec(prefix + r'spec.json$',         SwaggerResourcesHandler, default_settings, name=URL_SWAGGER_API_LIST),
        URLSpec(prefix + r'spec$',              SwaggerApiHandler,       default_settings, name=URL_SWAGGER_API_SPEC),
        (prefix + r'(.*\.(css|png|gif|js))',    StaticFileHandler,       { 'path': STATIC_PATH }),
    ]

