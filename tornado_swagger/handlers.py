#!/usr/bin/python
# -*- coding: utf-8 -*-
from tornado.web import URLSpec, StaticFileHandler

from tornado_swagger.settings import *
from tornado_swagger.views import *

__author__ = 'serena'


def swagger_handlers():
    prefix = default_settings.get('swagger_prefix', '/swagger')
    if prefix[-1] != '/':
        prefix += '/'
    return [
        URLSpec(prefix + r'spec.html$',         SwaggerUIHandler,        default_settings, name=URL_SWAGGER_API_DOCS),
        URLSpec(prefix + r'spec.json$',         SwaggerResourcesHandler, default_settings, name=URL_SWAGGER_API_LIST),
        URLSpec(prefix + r'spec$',              SwaggerApiHandler,       default_settings, name=URL_SWAGGER_API_SPEC),
        (prefix + r'(.*\.(css|png|gif|js))',    StaticFileHandler,       {'path': default_settings.get('static_path')}),
    ]
