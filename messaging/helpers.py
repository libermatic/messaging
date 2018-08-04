# -*- coding: utf-8 -*-

from functools import reduce
from toolz import assoc


QUERY_LIMIT = 10


def make_create(model, id_field, fields):
    def fn(body):
        if model.get_by_id(body.get(id_field)):
            raise ReferenceError()
        field_kwargs = _pick(fields, body)
        entity = model(
            id=body.get(id_field), **field_kwargs
        )
        entity.put()
        return entity.to_dict()
    return fn


def make_get(model):
    def fn(id):
        entity = model.get_by_id(id)
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


def make_update(model, fields):
    def fn(id, body):
        entity = model.get_by_id(id)
        if not entity:
            raise ReferenceError()
        field_kwargs = _pick(fields, body)
        if field_kwargs:
            entity.populate(**field_kwargs)
            entity.put()
        return entity.to_dict()
    return fn


def make_delete(model):
    def fn(id):
        entity = model.get_by_id(id)
        if not entity:
            raise ReferenceError()
        return entity.key.delete()
    return fn


def _pick(fields, from_dict):
    def set_field(a, x):
        if from_dict.get(x):
            return assoc(a, x, from_dict.get(x))
        return a
    return reduce(set_field, fields, {})
