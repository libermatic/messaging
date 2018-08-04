# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from toolz import merge

from messaging import helpers


class Service(ndb.Model):
    name = ndb.StringProperty(required=True)
    provider = ndb.KeyProperty('Account', required=True)
    quota = ndb.IntegerProperty()
    modified_at = ndb.DateTimeProperty(auto_now=True)

    def to_dict(self):
        return merge(
            super(Service, self).to_dict(exclude=['provider']),
            {
                'id': self.key.urlsafe(),
                'account': self.key.parent().id(),
                'provider': self.provider.id(),
            }
        )


def create(body, site):
    provider = ndb.Key('Provider', body.get('provider'))
    account = ndb.Key('Account', site)
    if not account.get() or not provider.get():
        raise ReferenceError()
    return helpers.make_create(
        Service, ['name', 'provider', 'quota', 'parent']
    )(
        merge(body, {'provider': provider, 'parent': account})
    )


def list(site=None):
    if site:
        entities = Service.query(ancestor=ndb.Key('Account', site)) \
            .order(Service.modified_at) \
            .fetch(limit=helpers.QUERY_LIMIT)
        return map(lambda x: x.to_dict(), entities)
    return helpers.make_list(Service)()


get = helpers.make_get(Service, urlsafe=True)
update = helpers.make_update(Service, ['name', 'quota'], urlsafe=True)
delete = helpers.make_delete(Service, urlsafe=True)
