# -*- coding: utf-8 -*-

from flask import request
from flask_restful import Resource, fields, marshal_with
from functools import partial
from toolz import compose


from messaging import helpers
from messaging.utils import omit
from messaging.models import accounts


resource_fields = {
    "site": fields.String,
    "name": fields.String,
    "modified_at": fields.DateTime(dt_format="iso8601"),
}

id_field = "site"
fields_to_omit = ["modified_at"]
create_fields = omit(fields_to_omit, resource_fields).keys()
update_fields = filter(lambda x: x != id_field, create_fields)


class Account(Resource):
    @marshal_with(resource_fields)
    def get(self, id):
        return helpers.make_get(accounts.Account)(id)

    @marshal_with(resource_fields)
    def put(self, id):
        return compose(
            partial(helpers.make_update(accounts.Account, update_fields), id),
            request.get_json,
        )()

    def delete(self, id):
        return helpers.make_delete(accounts.Account)(id), 204


class AccountList(Resource):
    @marshal_with(resource_fields)
    def get(self):
        return helpers.make_list(accounts.Account)()

    @marshal_with(resource_fields)
    def post(self):
        return (
            compose(
                helpers.make_create(accounts.Account, create_fields, id_field),
                request.get_json,
            )(),
            201,
        )


class AccountKey(Resource):
    def get(self, id):
        return {"api_key": accounts.generate_api_key(id)}
