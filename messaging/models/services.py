# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from toolz import merge, pluck

from messaging import helpers
from messaging.models.accounts import get_account_by_key
from messaging.dispatch import request
from messaging.models import messages
from messaging.exceptions import (
    EntityNotFound,
    ReferencedEntityNotFound,
    ServiceUnauthorized,
    ServiceMethodNotFound,
    ServiceBalanceDepleted,
)


class Service(ndb.Model):
    name = ndb.StringProperty(required=True)
    provider = ndb.KeyProperty(kind="Provider", required=True)
    vendor_key = ndb.StringProperty()
    quota = ndb.IntegerProperty()
    balance = ndb.IntegerProperty(default=0)
    unlimit = ndb.BooleanProperty(default=False)
    statics = ndb.JsonProperty(default=[])
    modified_at = ndb.DateTimeProperty(auto_now=True)

    def to_dict(self):
        return merge(
            super(Service, self).to_dict(exclude=["provider", "vendor_key"]),
            {
                "id": self.key.urlsafe(),
                "account": self.key.parent().id(),
                "provider": self.provider.id(),
            },
        )

    def get_static(self, field):
        try:
            static_fields = pluck("field", self.statics)
            index = list(static_fields).index(field)
            return merge(
                super(Service, self).to_dict(include=["name"]),
                {"id": self.key.urlsafe()},
                self.statics[index],
            )
        except ValueError:
            return None


def create(fields, account, provider, body, **args):
    if not account.get():
        raise ReferencedEntityNotFound("Account")
    if not provider.get():
        raise ReferencedEntityNotFound("Provider")
    return helpers.make_create(Service, fields + ["parent"])(
        merge(body, {"provider": provider, "parent": account}), **args
    )


def update(fields, service, provider, body, **args):
    if provider and not provider.get():
        raise ReferencedEntityNotFound("Provider")
    return helpers.make_update(Service, fields)(
        service, merge(body, {"provider": provider}) if provider else body, **args
    )


def delete(service):
    return helpers.delete(Service)(service)


def list_by_site(site):
    entities = (
        Service.query(ancestor=ndb.Key("Account", site))
        .order(Service.modified_at)
        .fetch(limit=helpers.QUERY_LIMIT)
    )
    return map(lambda x: x.to_dict(), entities)


def put_static(id, static):
    service = helpers.get_entity(Service, id)
    field = static.get("field")
    service.statics = filter(lambda x: x.get("field") != field, service.statics) + [
        static
    ]
    service.put()
    return service


def get_static(id, field):
    service = ndb.Key(urlsafe=id).get()
    if not service:
        raise EntityNotFound("Service")
    static = service.get_static(field)
    if not static:
        raise ReferenceError()
    return static


def remove_static(id, field):
    service = ndb.Key(urlsafe=id).get()
    if not service:
        raise EntityNotFound("Service")
    service.statics = filter(lambda x: x.get("field") != field, service.statics)
    service.put()
    return None


def _is_service_authorized(id, key=None):
    if not key:
        return False
    account = get_account_by_key(key)
    if not account:
        return False
    service = ndb.Key(urlsafe=id).get()
    if not service or service.key.parent() != account.key:
        return False
    return True


def call(id, action, body):
    if not _is_service_authorized(id, body.get("key")):
        raise ServiceUnauthorized()
    service = ndb.Key(urlsafe=id).get()
    provider = service.provider.get()
    method = provider.get_method(action)
    if not method:
        raise ServiceMethodNotFound("{} - {}".format(service.id, action))
    if not service.unlimit and service.balance <= 0:
        raise ServiceBalanceDepleted(id)
    res = request(service.vendor_key, service.statics, provider.config, method, body)
    if res.get("status") == "success":
        if not service.unlimit:
            service.balance -= res.get("cost", 1)
            service.put()
        if res.get("balance"):
            provider.balance = res.get("balance")
            provider.put()
    return messages.create(service.key, res)


def get_balance(id):
    service = ndb.Key(urlsafe=id).get()
    if not service:
        raise EntityNotFound("Service")
    return service.to_dict()


def reset_balance(id):
    service = ndb.Key(urlsafe=id).get()
    if not service:
        raise EntityNotFound("Service")
    service.balance = service.quota
    service.put()
    return service.to_dict()


def load_balance(id, amount):
    service = ndb.Key(urlsafe=id).get()
    if not service:
        raise EntityNotFound("Service")
    service.balance += amount
    service.put()
    return service.to_dict()
