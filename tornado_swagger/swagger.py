#!/usr/bin/python
# -*- coding: utf-8 -*-

import inspect
from functools import wraps
import epydoc.markup
import tornado.web
from settings import default_settings, models
from handlers import swagger_handlers

__author__ = 'serena'


class DocParser(object):
    def __init__(self):
        self.notes = None
        self.summary = None
        self.responseClass = None
        self.responseMessages = []
        self.params = {}
        self.properties = {}

    def parse_docstring(self, text):
        if text is None:
            return

        errors = []
        doc = epydoc.markup.parse(text, markup='epytext', errors=errors)
        _, fields = doc.split_fields(errors)

        for field in fields:
            tag = field.tag()
            arg = field.arg()
            body = field.body().to_plaintext(None).strip()
            self._get_parser(tag)(arg=arg, body=body)
        return doc

    def _get_parser(self, tag):
        parser = {
            'param': self._parse_param,
            'type': self._parse_type,
            'rtype': self._parse_rtype,
            'property': self._parse_property,
            'ptype': self._parse_ptype,
            'return': self._parse_return,
            'raise': self._parse_return,
            'notes': self._parse_notes,
            'description': self._parse_description,
        }
        return parser.get(tag, self._not_supported)

    def _parse_param(self, **kwargs):
        arg = kwargs.get('arg', None)
        body = kwargs.get('body', None)
        self.params.setdefault(arg, {}).update({
            'name': arg,
            'description': body,
            'paramType': arg,
            'required': True,
            'allowMultiple': False
        })

        if 'paramType' not in self.params[arg]:
            self.params[arg]['paramType'] = 'query'

    def _parse_type(self, **kwargs):
        arg = kwargs.get('arg', None)
        body = kwargs.get('body', None)
        self.params.setdefault(arg, {}).update({
            'name': arg,
            'dataType': body
        })

    def _parse_rtype(self, **kwargs):
        body = kwargs.get('body', None)
        self.responseClass = body

    def _parse_property(self, **kwargs):
        arg = kwargs.get('arg', None)
        self.properties.setdefault(arg, {}).update({
            'type': 'string'
        })

    def _parse_ptype(self, **kwargs):
        arg = kwargs.get('arg', None)
        body = kwargs.get('body', None)
        self.properties.setdefault(arg, {}).update({
            'type': body
        })

    def _parse_return(self, **kwargs):
        arg = kwargs.get('arg', None)
        body = kwargs.get('body', None)
        self.responseMessages.append({
            'code': arg,
            'message': body
        })

    def _parse_notes(self, **kwargs):
        body = kwargs.get('body', '')
        self.notes = self._sanitize_doc(body)

    def _parse_description(self, **kwargs):
        body = kwargs.get('body', '')
        self.summary = self._sanitize_doc(body)

    def _not_supported(self, **kwargs):
        pass

    @staticmethod
    def _sanitize_doc(comment):
        return comment.replace('\n', '<br/>') if comment else comment


class model(DocParser):
    def __init__(self, cls=None, *args, **kwargs):
        super(model, self).__init__()
        self.id = cls.__name__
        self.args = args
        self.kwargs = kwargs
        self.required = []

        if '__init__' in dir(cls):
            self._parse_args(cls.__init__)
        self.parse_docstring(inspect.getdoc(cls))
        models.append(self)

    def _parse_args(self, func):
        argspec = inspect.getargspec(func)
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



class operation(DocParser):
    def __init__(self, nickname=None, **kwds):
        super(operation, self).__init__()
        self.nickname = nickname
        self.func = None
        self.func_args = []
        self.kwds = kwds

    def __call__(self, *args, **kwds):
        if self.func:
            return self.func(*args, **kwds)

        func = args[0]
        self._parse_operation(func)

        @wraps(func)
        def __wrapper__(*in_args, **in_kwds):
            return self.func(*in_args, **in_kwds)

        __wrapper__.rest_api = self
        return __wrapper__

    def _parse_operation(self, func):
        self.func = func

        self.__name__ = func.__name__
        self._parse_args(func)
        self.parse_docstring(inspect.getdoc(self.func))

    def _parse_args(self, func):
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
        self.func_args = argspec.args


def docs(**opts):
    default_settings.update(opts)


class Application(tornado.web.Application):
    def __init__(self, handlers=None, default_host="", transforms=None, **settings):
        super(Application, self).__init__(swagger_handlers() + handlers, default_host, transforms, **settings)
