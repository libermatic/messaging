# -*- coding: utf-8 -*-

from google.appengine.ext import ndb


class User(ndb.Model):
    email = ndb.StringProperty(required=True)
    name = ndb.StringProperty()
    password_hash = ndb.StringProperty(required=True)
    modified_at = ndb.DateTimeProperty(auto_now=True)

    _excluded_keys = ["password_hash"]

    def to_dict(self):
        return super(User, self).to_dict(exclude=self._excluded_keys)
