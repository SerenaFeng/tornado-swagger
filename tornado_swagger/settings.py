#!/usr/bin/python
# -*- coding: utf-8 -*-
import os.path

__author__ = 'serena'

SWAGGER_VERSION = '1.2'

URL_SWAGGER_API_DOCS = 'swagger-api-docs'
URL_SWAGGER_API_LIST = 'swagger-api-list'
URL_SWAGGER_API_SPEC = 'swagger-api-spec'

STATIC_PATH = os.path.join(os.path.dirname(os.path.normpath(__file__)), 'static')

default_settings = {
    'base_url': '/',
    'static_path': STATIC_PATH,
    'swagger_prefix': '/swagger',
    'api_version': 'v1.0',
    'api_key': '',
    'enabled_methods': ['get', 'post', 'put', 'patch', 'delete'],
    'exclude_namespaces': [],
}

models = []
