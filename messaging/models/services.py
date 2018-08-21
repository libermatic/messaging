# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from toolz import merge, concatv

from messaging import helpers


class Service(ndb.Model):
    name = ndb.StringProperty(required=True)
    provider = ndb.KeyProperty('Provider', required=True)
    vendor_key = ndb.StringProperty()
    quota = ndb.IntegerProperty()
    balance = ndb.IntegerProperty(default=0)
    modified_at = ndb.DateTimeProperty(auto_now=True)

    def to_dict(self):
        return merge(
            super(Service, self).to_dict(exclude=['provider', 'vendor_key']),
            {
                'id': self.key.urlsafe(),
                'account': self.key.parent().id(),
                'provider': self.provider.id(),
            }
        )


def create(fields, site, body):
    account = ndb.Key('Account', site)
    provider = ndb.Key('Provider', body.get('provider'))
    if not account.get() or not provider.get():
        raise ReferenceError()
    return helpers.make_create(
        Service, concatv(fields, ['parent']),
    )(
        merge(body, {'provider': provider, 'parent': account})
    )


def update(fields, id, body):
    provider = body.get('provider')
    if provider and not ndb.Key('Provider', provider).get():
        raise ReferenceError()
    return helpers.make_update(Service, fields, urlsafe=True)(
        id,
        merge(body, {'provider': ndb.Key('Provider', provider)})
        if provider else body,
    )


def list_by_site(site=None):
    entities = Service.query(ancestor=ndb.Key('Account', site)) \
        .order(Service.modified_at) \
        .fetch(limit=helpers.QUERY_LIMIT)
    return map(lambda x: x.to_dict(), entities)
