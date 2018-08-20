# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
import requests
from toolz import merge

from messaging import helpers
from messaging.accounts import get_account_by_key


class Message(ndb.Model):
    modified_at = ndb.DateTimeProperty(auto_now=True)
    response = ndb.StringProperty()

    def to_dict(self):
        return merge(
            super(Message, self).to_dict(),
            {
                'id': self.key.urlsafe(),
                'service': self.key.parent().urlsafe(),
            }
        )


def create(body, service_id):
    account = get_account_by_key(body.get('api_key'))
    if not account:
        raise ReferenceError('INVALID_USER')
    service = ndb.Key(urlsafe=service_id).get()
    if not service or service.key.parent() != account.key:
        raise ReferenceError()
    if service.balance <= 0:
        raise ValueError
    service.balance -= 1
    service.put()
    r = requests.get('http://www.google.com')
    print(r.text)
    return helpers.make_create(Message, ['response', 'parent'])(
        merge(body, {'parent': service.key})
    )
