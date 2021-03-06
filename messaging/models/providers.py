# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from toolz import merge, dissoc

from messaging import helpers
from messaging.exceptions import ReferencedEntityNotFound


class Provider(ndb.Model):
    name = ndb.StringProperty(required=True)
    balance = ndb.IntegerProperty(default=0)
    type = ndb.StringProperty(choices=["text"])
    base_url = ndb.StringProperty(required=True)
    methods = ndb.JsonProperty(default={})
    config = ndb.JsonProperty(default={})
    modified_at = ndb.DateTimeProperty(auto_now=True)

    def to_dict(self):
        return merge(
            super(Provider, self).to_dict(exclude=["methods"]),
            {"methods": self.methods.values()},
        )

    def get_method(self, action):
        method = self.methods.get(action)
        return (
            merge(super(Provider, self).to_dict(include=["name", "base_url"]), method)
            if method
            else None
        )


def create(fields, user, body, **args):
    if not user.get():
        raise ReferencedEntityNotFound("User")
    return helpers.make_create(Provider, fields + ["parent"], "name")(
        merge(body, {"parent": user}), **args
    )


def update(fields, provider, body, **args):
    return helpers.make_update(Provider, fields)(provider, body, **args)


def delete(provider):
    return helpers.make_delete(Provider)(provider)


def put_method(id, method):
    provider = helpers.get_entity(Provider, id)
    action = method.get("action")
    provider.methods = merge(provider.methods or {}, {action: method})
    provider.put()
    return provider


def remove_method(id, action):
    provider = helpers.get_entity(Provider, id)
    provider.methods = dissoc(provider.methods or {}, action)
    provider.put()
    return provider


def put_config(id, config):
    provider = helpers.get_entity(Provider, id)
    provider.config = merge(provider.config or {}, config)
    provider.put()
    return provider
