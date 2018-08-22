# -*- coding: utf-8 -*-


from flask_restful import Resource, fields, marshal_with

from messaging.models import messages
from messaging import helpers


resource_fields = {
    'id': fields.String,
    'status': fields.String,
    'cost': fields.Integer,
    'modified_at': fields.DateTime(dt_format='iso8601'),
}


class MessageList(Resource):
    @marshal_with(resource_fields)
    def get(self, service):
        return messages.list_by_service(service)


class MessageAll(Resource):
    @marshal_with(resource_fields)
    def get(self):
        return helpers.make_list(messages.Message)()
