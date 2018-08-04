# -*- coding: utf-8 -*-

import os
import hashlib
from google.appengine.ext import ndb

from messaging import helpers


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


create = helpers.make_create(Account, ['site', 'name'], 'site')
get = helpers.make_get(Account)
list = helpers.make_list(Account)
update = helpers.make_update(Account, ['name'])
delete = helpers.make_delete(Account)


def generate_api_key(id):
    account = Account.get_by_id(id)
    if not account:
        raise ReferenceError()
    api_key = account.generate_api_key()
    return {'site': account.site, 'api_key': api_key}
