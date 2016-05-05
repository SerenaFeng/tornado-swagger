#!/usr/bin/python
# -*- coding: utf-8 -*-

import inspect
from functools import wraps
import epydoc.markup

__author__ = 'serena'

models = []

class DocParser(object):
    def __init__(self):
        self.notes = None
        self.summary = None
        self.responseClass = None
        self.responseMessages = []
        self.params = {}

    @staticmethod
    def _sanitize_doc(comment):
        return comment.replace('\n', '<br/>') if comment else comment

    def parse_docstring(self, text):
        errors = []

        doc = epydoc.markup.parse(text, markup='epytext', errors=errors)

        _, fields = doc.split_fields(errors)

        for field in fields:
            tag = field.tag()
            arg = field.arg()
            body = field.body().to_plaintext(None).strip()
            if tag == 'param':
                self.params.setdefault(arg, {}).update({
                    'name': arg,
                    'description': body,
                    'paramType': arg,
                    'required': True,
                    'allowMultiple': False
                })

                if 'paramType' not in self.params[arg]:
                    self.params[arg]['paramType'] = 'query'
            elif field.tag() == 'type':
                self.params.setdefault(arg, {}).update({
                    'name': arg,
                    'dataType': body
                })
            elif field.tag() == 'rtype':
                self.responseClass = body
            elif field.tag() == 'return' or field.tag() == 'raise':
                self.responseMessages.append({
                    'code': arg,
                    'message': body
                })
            elif field.tag() == 'notes':
                self.notes = self._sanitize_doc(body)
            elif field.tag() == 'description':
                self.summary = self._sanitize_doc(body)
        return doc


class model(DocParser):
    def __init__(self, cls=None, *args, **kwargs):
        super(model, self).__init__(**kwargs)
        self.id = cls.__name__
        self.args = args
        self.kwargs = kwargs
        self.properties = {}
        self.required = []

        if '__init__' in dir(cls):
            argspec = inspect.getargspec(cls.__init__)
            argspec.args.remove("self")
            defaults = {}
            if argspec.defaults:
                defaults = list(zip(argspec.args[-len(argspec.defaults):], argspec.defaults))
            required_args_count = len(argspec.args) - len(defaults)
            for arg in argspec.args[:required_args_count]:
                self.required.append(arg)
                self.properties.setdefault(arg, {'type': 'string'})
            for arg, default in defaults:
                self.properties.setdefault(arg, {'type': 'string', "default": default})
        self.parse_docstring(inspect.getdoc(cls))
        models.append(self)

class operation(DocParser):
    def __init__(self, nickname=None, **kwds):
        super(operation, self).__init__()
        self.nickname = nickname
        self.func = None
        self.func_args = []
        self.kwds = kwds

    def __bind__(self, func):
        self.func = func
        self.__name__ = func.__name__
        argspec = inspect.getargspec(func)
        argspec.args.remove("self")

        defaults = []
        if argspec.defaults:
            defaults = argspec.args[-len(argspec.defaults):]

        for arg in argspec.args:
            if arg in defaults:
                required = False
            else:
                required = True
            self.params.setdefault(arg, {
                'name': arg,
                'required': required,
                'paramType': 'path',
                'dataType': 'string'
            })

        self.parse_docstring(inspect.getdoc(self.func))
        self.func_args = argspec.args

    def __call__(self, *args, **kwds):
        if self.func:
            return self.func(*args, **kwds)

        func = args[0]

        self.__bind__(func)

        @wraps(func)
        def __wrapper__(*args, **kwds):
            return self.func(*args, **kwds)

        __wrapper__.rest_api = self

        return __wrapper__


def find_api(host_handlers):
    for host, handlers in host_handlers:
        for spec in handlers:
            for (name, member) in inspect.getmembers(spec.handler_class):
                if inspect.ismethod(member) and hasattr(member, 'rest_api'):
                    spec_path = spec._path % tuple(['{%s}' % arg for arg in member.rest_api.func_args])
                    operations = [member.rest_api for (name, member) in inspect.getmembers(spec.handler_class) if hasattr(member, 'rest_api')]
                    yield spec_path, spec, operations
                    break

def find_models():
    return models
