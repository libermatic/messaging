# -*- coding: utf-8 -*-

from flask import request
from google.appengine.api.datastore_errors import (
    BadValueError, BadRequestError
)
from flask_restful import Resource, abort, fields, marshal_with, reqparse
from functools import partial
from toolz import compose, remove, keyfilter, merge

from messaging import helpers, error_responses
from messaging.models import providers


method_fields = {
    'action': fields.String,
    'method': fields.String,
    'path': fields.String,
    'args': fields.List(fields.String),
}
resource_fields = {
    'name': fields.String,
    'type': fields.String,
    'base_url': fields.String,
    'methods': fields.List(fields.Nested(method_fields)),
    'modified_at': fields.DateTime(dt_format='iso8601'),
}

id_field = 'name'
create_fields = remove(
    lambda x: x == 'modified_at', resource_fields.keys()
)
update_fields = remove(lambda x: x == id_field, create_fields)


class Provider(Resource):
    @marshal_with(resource_fields)
    def get(self, id):
        try:
            return helpers.make_get(providers.Provider)(id)
        except ReferenceError:
            return abort(404, message=error_responses.NOT_FOUND)

    @marshal_with(resource_fields)
    def put(self, id):
        try:
            return compose(
                partial(
                    helpers.make_update(providers.Provider, update_fields),
                    id,
                ),
                request.get_json,
            )()
        except ReferenceError:
            return abort(404, message=error_responses.NOT_FOUND)

    def delete(self, id):
        try:
            return helpers.make_delete(providers.Provider)(id), 204
        except ReferenceError:
            return abort(404, message=error_responses.NOT_FOUND)

    def post(self, id):
        pass


class ProviderList(Resource):
    @marshal_with(resource_fields)
    def get(self):
        return helpers.make_list(providers.Provider)()

    @marshal_with(resource_fields)
    def post(self):
        try:
            return compose(
                helpers.make_create(
                    providers.Provider, create_fields, id_field,
                ),
                request.get_json,
            )(), 201
        except (BadValueError, BadRequestError):
            return abort(400, message=error_responses.INVALID_FIELD)
        except ReferenceError:
            return abort(409, message=error_responses.ALREADY_EXISTS)


method_parser = reqparse.RequestParser()
method_parser.add_argument(
    'action', required=True, help=error_responses.INVALID_FIELD,
)
method_parser.add_argument('method', choices=['get', 'post'])
method_parser.add_argument('path')
method_parser.add_argument('args', action='append')


single_method_fields = merge(
    keyfilter(lambda x: x in ['name', 'base_url'], resource_fields),
    method_fields,
)


class ProviderMethod(Resource):
    @marshal_with(single_method_fields)
    def get(self, id, action):
        try:
            return providers.get_method(id, action)
        except ReferenceError:
            return abort(404, message=error_responses.NOT_FOUND)

    def delete(self, id, action):
        try:
            return providers.remove_method(id, action), 204
        except ReferenceError:
            return abort(404, message=error_responses.NOT_FOUND)


class ProviderMethodPut(Resource):
    @marshal_with(single_method_fields)
    def post(self, id):
        try:
            return compose(
                partial(providers.put_method, id),
                method_parser.parse_args,
            )()
        except ReferenceError:
            return abort(404, message=error_responses.NOT_FOUND)
