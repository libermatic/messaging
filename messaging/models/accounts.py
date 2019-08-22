# -*- coding: utf-8 -*-

import os
import hashlib
from google.appengine.ext import ndb
from toolz import merge, pluck

from messaging import helpers
from messaging.exceptions import EntityNotFound, ReferencedEntityNotFound


class Account(ndb.Model):
    site = ndb.StringProperty(required=True)
    name = ndb.StringProperty()
    user = ndb.KeyProperty(kind="User", required=True)
    modified_at = ndb.DateTimeProperty(auto_now=True)
    key_hash = ndb.StringProperty()

    _excluded_keys = ["key_hash"]

    def to_dict(self):
        return super(Account, self).to_dict(exclude=self._excluded_keys)

    def generate_api_key(self):
        api_key = os.urandom(24).encode("hex")
        self.key_hash = hashlib.sha1(api_key).hexdigest()
        self.put()
        return api_key


def generate_api_key(id):
    account = Account.get_by_id(id)
    if not account:
        raise EntityNotFound("Account")
    return account.generate_api_key()


def create(fields, user, body, **args):
    if not user.get():
        raise ReferencedEntityNotFound("User not found")
    return helpers.make_create(Account, fields + ["parent"])(
        merge(body, {"parent": user}), **args
    )


def get_account_by_key(key):
    if not key:
        return None
    key_hash = hashlib.sha1(key).hexdigest()
    try:
        return Account.query(Account.key_hash == key_hash).fetch(limit=1)[0]
    except IndexError:
        return None
