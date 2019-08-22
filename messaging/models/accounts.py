# -*- coding: utf-8 -*-

import os
import hashlib
from google.appengine.ext import ndb

from messaging.exceptions import EntityNotFound


class Account(ndb.Model):
    site = ndb.StringProperty(required=True)
    name = ndb.StringProperty()
    password_hash = ndb.StringProperty()
    modified_at = ndb.DateTimeProperty(auto_now=True)
    key_hash = ndb.StringProperty()

    _excluded_keys = ["password_hash", "key_hash"]

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


def get_account_by_key(key):
    if not key:
        return None
    key_hash = hashlib.sha1(key).hexdigest()
    try:
        return Account.query(Account.key_hash == key_hash).fetch(limit=1)[0]
    except IndexError:
        return None
