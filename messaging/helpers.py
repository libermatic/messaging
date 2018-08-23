# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from functools import reduce
from toolz import assoc

from messaging.utils import pick

QUERY_LIMIT = 10


def make_create(model, fields, id_field=None):
    if type(fields) is not list:
        raise TypeError('fields needs to be a list')

    def fn(body):
        if id_field and model.get_by_id(body.get(id_field)):
            raise ReferenceError()
        field_kwargs = assoc(pick(fields, body), 'id', body.get(id_field)) \
            if id_field else pick(fields, body)
        entity = model(**field_kwargs)
        entity.put()
        return entity.to_dict()
    return fn


def make_get(model, urlsafe=False):
    def fn(id):
        entity = ndb.Key(urlsafe=id).get() \
            if urlsafe else model.get_by_id(id)
        if not entity:
            raise ReferenceError()
        return entity.to_dict()
    return fn


def make_list(model):
    def fn():
        entities = model.query() \
            .order(model.modified_at) \
            .fetch(limit=QUERY_LIMIT)
        return map(lambda x: x.to_dict(), entities)
    return fn


def make_update(model, fields, urlsafe=False):
    def fn(id, body):
        entity = ndb.Key(urlsafe=id).get() \
            if urlsafe else model.get_by_id(id)
        if not entity:
            raise ReferenceError()
        field_kwargs = pick(fields, body)
        if field_kwargs:
            entity.populate(**field_kwargs)
            entity.put()
        return entity.to_dict()
    return fn


def make_delete(model, urlsafe=False):
    def fn(id):
        entity = ndb.Key(urlsafe=id).get() \
            if urlsafe else model.get_by_id(id)
        if not entity:
            raise ReferenceError()
        return entity.key.delete()
    return fn
