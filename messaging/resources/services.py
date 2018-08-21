# -*- coding: utf-8 -*-

from flask import request
from google.appengine.api.datastore_errors import (
    BadValueError, BadRequestError
)
from flask_restful import Resource, abort, fields, marshal_with
from functools import partial
from toolz import compose, remove, concatv


from messaging import helpers, error_responses
from messaging.models import services


resource_fields = {
    'id': fields.String,
    'name': fields.String,
    'account': fields.String,
    'provider': fields.String,
    'quota': fields.Integer,
    'balance': fields.Integer,
    'modified_at': fields.DateTime(dt_format='iso8601'),
}

update_fields = concatv(
    remove(
        lambda x: x in ['id', 'modified_at', 'account', 'balance'],
        resource_fields.keys(),
    ),
    ['vendor_key']
)


class Service(Resource):
    @marshal_with(resource_fields)
    def get(self, id):
        try:
            return helpers.make_get(services.Service, urlsafe=True)(id)
        except ReferenceError:
            return abort(404, message=error_responses.NOT_FOUND)

    @marshal_with(resource_fields)
    def put(self, id):
        try:
            return compose(
                partial(services.update, update_fields, id),
                request.get_json,
            )()
        except ReferenceError:
            return abort(404, message=error_responses.REF_NOT_FOUND)

    def delete(self, id):
        try:
            return helpers.make_delete(services.Service, urlsafe=True)(id), 204
        except ReferenceError:
            return abort(404, message=error_responses.NOT_FOUND)


class ServiceList(Resource):
    @marshal_with(resource_fields)
    def get(self, site):
        return services.list_by_site(site)

    @marshal_with(resource_fields)
    def post(self, site):
        try:
            return compose(
                partial(services.create, update_fields, site),
                request.get_json,
            )(), 201
        except (BadValueError, BadRequestError):
            return abort(400, message=error_responses.INVALID_FIELD)
        except ReferenceError:
            return abort(404, message=error_responses.REF_NOT_FOUND)


class ServiceAll(Resource):
    @marshal_with(resource_fields)
    def get(self):
        return helpers.make_list(services.Service)()
