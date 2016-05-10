#!/usr/bin/python
# -*- coding: utf-8 -*-
import urlparse
import json
import inspect
import tornado.web
import tornado.template
from tornado_swagger.settings import SWAGGER_VERSION, URL_SWAGGER_API_LIST, URL_SWAGGER_API_SPEC, models

__author__ = 'serena'


def json_dumps(obj, pretty=False):
    return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': ')) if pretty else json.dumps(obj)


class SwaggerUIHandler(tornado.web.RequestHandler):
    def initialize(self, static_path, **kwds):
        self.static_path = static_path

    def get_template_path(self):
        return self.static_path

    def get(self):
        discovery_url = urlparse.urljoin(self.request.full_url(), self.reverse_url(URL_SWAGGER_API_LIST))
        self.render('index.html', discovery_url=discovery_url)


class SwaggerResourcesHandler(tornado.web.RequestHandler):
    def initialize(self, api_version, exclude_namespaces, **kwds):
        self.api_version = api_version
        self.exclude_namespaces = exclude_namespaces

    def get(self):
        self.set_header('content-type', 'application/json')
        u = urlparse.urlparse(self.request.full_url())
        resources = {
            'apiVersion': self.api_version,
            'swaggerVersion': SWAGGER_VERSION,
            'basePath': '%s://%s' % (u.scheme, u.netloc),
            'produces': ["application/json"],
            'description': 'Test Api Spec',
            'apis': [{
                'path': self.reverse_url(URL_SWAGGER_API_SPEC),
                'description': 'Test Api Spec'
            }]
        }

        self.finish(json_dumps(resources, self.get_arguments('pretty')))


class SwaggerApiHandler(tornado.web.RequestHandler):
    def initialize(self, api_version, base_url, **kwds):
        self.api_version = api_version
        self.base_url = base_url

    def get(self):
        self.set_header('content-type', 'application/json')
        apis = self.find_api(self.application.handlers)
        if apis is None:
            raise tornado.web.HTTPError(404)

        specs = {
            'apiVersion': self.api_version,
            'swaggerVersion': SWAGGER_VERSION,
            'basePath': urlparse.urljoin(self.request.full_url(), self.base_url)[:-1],
            'apis': [self.__get_api_spec__(path, spec, operations) for path, spec, operations in apis],
            'models': self.__get_models_spec(models)
        }
        self.finish(json_dumps(specs, self.get_arguments('pretty')))

    def __get_models_spec(self, models):
        models_spec = {}
        for model in models:
            models_spec.setdefault(model.id, self.__get_model_spec(model))
        return models_spec

    @staticmethod
    def __get_model_spec(model):
        return {
            'description': model.summary,
            'id': model.id,
            'notes': model.notes,
            'properties': model.properties,
            'required': model.required
        }

    @staticmethod
    def __get_api_spec__(path, spec, operations):
        return {
            'path': path,
            'description': spec.handler_class.__doc__,
            'operations': [{
                'httpMethod': api.func.__name__.upper(),
                'nickname': api.nickname,
                'parameters': api.params.values(),
                'summary': api.summary,
                'notes': api.notes,
                'responseClass': api.responseClass,
                'responseMessages': api.responseMessages,
            } for api in operations]
        }

    @staticmethod
    def find_api(host_handlers):
        for host, handlers in host_handlers:
            for spec in handlers:
                for (name, member) in inspect.getmembers(spec.handler_class):
                    if inspect.ismethod(member) and hasattr(member, 'rest_api'):
                        spec_path = spec._path % tuple(['{%s}' % arg for arg in member.rest_api.func_args])
                        operations = [member.rest_api for (name, member) in inspect.getmembers(spec.handler_class)
                                      if hasattr(member, 'rest_api')]
                        yield spec_path, spec, operations
                        break


