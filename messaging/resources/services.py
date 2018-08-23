# -*- coding: utf-8 -*-

from flask import request
from flask_restful import Resource, fields, marshal_with, reqparse
from functools import partial
from toolz import compose, merge


from messaging import helpers
from messaging.utils import omit, pick
from messaging.models import services
from messaging.resources import messages

static_fields = {
    'field': fields.String(),
    'value': fields.String(),
    'location': fields.String(),
}
resource_fields = {
    'id': fields.String,
    'name': fields.String,
    'account': fields.String,
    'provider': fields.String,
    'quota': fields.Integer,
    'balance': fields.Integer,
    'statics': fields.List(fields.Nested(static_fields)),
    'modified_at': fields.DateTime(dt_format='iso8601'),
}

update_fields = omit(
    ['id', 'modified_at', 'account', 'balance', 'statics'],
    resource_fields,
).keys() + ['vendor_key']


class Service(Resource):
    @marshal_with(resource_fields)
    def get(self, id):
        return helpers.make_get(services.Service, urlsafe=True)(id)

    @marshal_with(resource_fields)
    def put(self, id):
        return compose(
            partial(services.update, update_fields, id),
            request.get_json,
        )()

    def delete(self, id):
        return helpers.make_delete(services.Service, urlsafe=True)(id), 204


class ServiceList(Resource):
    @marshal_with(resource_fields)
    def get(self, site):
        return services.list_by_site(site)

    @marshal_with(resource_fields)
    def post(self, site):
        return compose(
            partial(services.create, update_fields, site),
            request.get_json,
        )(), 201


static_parser = reqparse.RequestParser()
static_parser.add_argument('field', required=True)
static_parser.add_argument('value')
static_parser.add_argument(
    'location', choices=['header', 'body', 'query'], required=True,
)

single_static_fields = merge(
    pick(['id', 'name'], resource_fields),
    static_fields,
)


class ServiceStatic(Resource):
    @marshal_with(single_static_fields)
    def get(self, id, field):
        return services.get_static(id, field)

    def delete(self, id, field):
        return services.remove_static(id, field), 204


class ServiceStaticPut(Resource):
    @marshal_with(single_static_fields)
    def post(self, id):
        return compose(
            partial(services.put_static, id),
            static_parser.parse_args,
        )()


class ServiceAll(Resource):
    @marshal_with(resource_fields)
    def get(self):
        return helpers.make_list(services.Service)()


class ServiceAction(Resource):
    @marshal_with(messages.resource_fields)
    def post(self, id, action):
        return compose(
            partial(services.call, id, action),
            request.get_json
        )()
