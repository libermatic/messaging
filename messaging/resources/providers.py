# -*- coding: utf-8 -*-

from flask import request
from flask_restful import Resource, fields, marshal_with, reqparse
from functools import partial
from toolz import compose, merge

from messaging import helpers
from messaging.utils import omit, pick
from messaging.models import providers


method_fields = {
    'action': fields.String,
    'method': fields.String,
    'path': fields.String,
    'args': fields.List(fields.String),
}
config_fields = {
    'auth_label': fields.String,
    'auth_location': fields.String,
    'error_condition': fields.String,
    'cost_field': fields.String,
    'balance_field': fields.String,
    'error_field': fields.String,
}
resource_fields = {
    'name': fields.String,
    'type': fields.String,
    'balance': fields.Integer,
    'base_url': fields.String,
    'methods': fields.List(fields.Nested(method_fields)),
    'config': fields.Nested(config_fields),
    'modified_at': fields.DateTime(dt_format='iso8601'),
}

id_field = 'name'
fields_to_omit = ['methods', 'config', 'balance', 'modified_at']
create_fields = omit(fields_to_omit, resource_fields).keys()
update_fields = filter(lambda x: x != id_field, create_fields)


class Provider(Resource):
    @marshal_with(resource_fields)
    def get(self, id):
        return helpers.make_get(providers.Provider)(id)

    @marshal_with(resource_fields)
    def put(self, id):
        return compose(
            partial(
                helpers.make_update(providers.Provider, update_fields),
                id,
            ),
            request.get_json,
        )()

    def delete(self, id):
        return helpers.make_delete(providers.Provider)(id), 204


class ProviderList(Resource):
    @marshal_with(resource_fields)
    def get(self):
        return helpers.make_list(providers.Provider)()

    @marshal_with(resource_fields)
    def post(self):
        return compose(
            helpers.make_create(
                providers.Provider, create_fields, id_field,
            ),
            request.get_json,
        )(), 201


method_parser = reqparse.RequestParser()
method_parser.add_argument('action', required=True)
method_parser.add_argument('method', choices=['GET', 'POST'])
method_parser.add_argument('path')
method_parser.add_argument('args', action='append')


single_method_fields = merge(
    pick(['name', 'base_url'], resource_fields),
    method_fields,
)


class ProviderMethod(Resource):
    @marshal_with(single_method_fields)
    def get(self, id, action):
        return providers.get_method(id, action)

    def delete(self, id, action):
        return providers.remove_method(id, action), 204


class ProviderMethodPut(Resource):
    @marshal_with(single_method_fields)
    def post(self, id):
        return compose(
            partial(providers.put_method, id),
            method_parser.parse_args,
        )()


config_parser = reqparse.RequestParser()
config_parser.add_argument('auth_label', required=True)
config_parser.add_argument(
    'auth_location', choices=['header', 'body', 'query'], required=True,
)
config_parser.add_argument('error_condition', type=dict)
config_parser.add_argument('error_field')
config_parser.add_argument('cost_field')
config_parser.add_argument('balance_field')

single_config_fields = pick(['name', 'config'], resource_fields)


class ProviderConfigPut(Resource):
    @marshal_with(single_config_fields)
    def post(self, id):
        return compose(
            partial(providers.put_config, id),
            config_parser.parse_args,
        )()
