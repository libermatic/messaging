# -*- coding: utf-8 -*-

import os
import hashlib
from google.appengine.ext import ndb
from functools import reduce
from toolz import assoc


QUERY_LIMIT = 10


class Account(ndb.Model):
    site = ndb.StringProperty(required=True)
    name = ndb.StringProperty()
    modified_at = ndb.DateTimeProperty(auto_now=True)
    key_hash = ndb.StringProperty()

    def to_dict(self):
        return super(Account, self).to_dict(exclude=['key_hash'])

    def generate_api_key(self):
        api_key = os.urandom(24).encode('hex')
        self.key_hash = hashlib.sha1(api_key).hexdigest()
        self.put()
        return api_key


def create(body, with_key=False):
    if Account.get_by_id(body.get('site')):
        raise ReferenceError()
    account = Account(
        id=body.get('site'),
        site=body.get('site'),
        name=body.get('name'),
    )
    account.put()
    return account.to_dict()


def get(id):
    account = Account.get_by_id(id)
    if not account:
        raise ReferenceError()
    return account.to_dict()


def update(id, body):
    account = Account.get_by_id(id)
    if not account:
        raise ReferenceError()

    def set_field(a, x):
        if body.get(x):
            return assoc(a, x, body.get(x))
        return a
    kwargs = reduce(set_field, ['name'], {})
    if kwargs:
        account.populate(**kwargs)
        account.put()
    return account.to_dict()


def delete(id):
    account = Account.get_by_id(id)
    if not account:
        raise ReferenceError()
    return account.key.delete()


def list():
    accounts = Account.query() \
        .order(Account.modified_at) \
        .fetch(limit=QUERY_LIMIT)
    return map(lambda x: x.to_dict(), accounts)
