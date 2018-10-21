# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from toolz import merge

from messaging import helpers
from messaging.exceptions import ServiceCallFailure


class Message(ndb.Model):
    response = ndb.JsonProperty()
    status = ndb.StringProperty(choices=['success', 'failure'])
    cost = ndb.IntegerProperty()
    modified_at = ndb.DateTimeProperty(auto_now=True)

    def to_dict(self):
        return merge(
            super(Message, self).to_dict(exclude=['response']),
            {
                'id': self.key.urlsafe(),
                'service': self.key.parent().urlsafe(),
            }
        )


def create(service_key, body):
    req_has_failed = body.get('status') == 'failure'
    fields = ['status', 'cost', 'parent']
    message = helpers.make_create(
        Message, fields + ['response'] if req_has_failed else fields,
    )(
        merge(body, {'parent': service_key})
    )
    if req_has_failed:
        raise ServiceCallFailure(
            "{} - {}: {}".format(service_key.id(), message.get('id'), body)
        )
    return message


def list_by_service(service):
    entities = Message.query(ancestor=ndb.Key(urlsafe=service)) \
        .order(Message.modified_at) \
        .fetch(limit=helpers.QUERY_LIMIT)
    return map(lambda x: x.to_dict(), entities)
