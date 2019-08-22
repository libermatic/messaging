# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from toolz import assoc

from messaging.utils import pick
from messaging.exceptions import EntityAlreadyExists, EntityNotFound, InvalidField


QUERY_LIMIT = 10


def make_create(model, fields, id_field=None):
    if type(fields) is not list:
        raise TypeError("fields needs to be a list")

    def fn(body, as_obj=False):
        try:
            if id_field and model.get_by_id(body.get(id_field)):
                raise EntityAlreadyExists(model.__name__)
        except TypeError as e:
            raise InvalidField(*e)
        field_kwargs = (
            assoc(pick(fields, body), "id", body.get(id_field))
            if id_field
            else pick(fields, body)
        )
        entity = model(**field_kwargs)
        entity.put()
        return entity if as_obj else entity.to_dict()

    return fn


def make_get(model, urlsafe=False):
    def fn(id, as_obj=False):
        try:
            entity = ndb.Key(urlsafe=id).get() if urlsafe else model.get_by_id(id)
        except TypeError as e:
            raise InvalidField(*e)
        if not entity:
            raise EntityNotFound(model.__name__)
        return entity if as_obj else entity.to_dict()

    return fn


def make_list(model):
    def fn():
        entities = model.query().order(model.modified_at).fetch(limit=QUERY_LIMIT)
        return map(lambda x: x.to_dict(), entities)

    return fn


def make_update(model, fields, urlsafe=False):
    def fn(id, body, as_obj=False):
        try:
            entity = ndb.Key(urlsafe=id).get() if urlsafe else model.get_by_id(id)
        except TypeError as e:
            raise InvalidField(*e)
        if not entity:
            raise EntityNotFound(model.__name__)
        field_kwargs = pick(fields, body)
        if field_kwargs:
            entity.populate(**field_kwargs)
            entity.put()
        return entity if as_obj else entity.to_dict()

    return fn


def make_delete(model, urlsafe=False):
    def fn(id):
        try:
            entity = ndb.Key(urlsafe=id).get() if urlsafe else model.get_by_id(id)
        except TypeError as e:
            raise InvalidField(*e)
        if not entity:
            raise EntityNotFound(model.__name__)
        return entity.key.delete()

    return fn
