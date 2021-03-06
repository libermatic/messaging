# -*- coding: utf-8 -*-

from flask import request
from functools import partial
from toolz import compose

from messaging.models import services
from messaging.utils import omit
from messaging.exceptions import UnsupportedContent


def get_balance(id):
    return services.get_balance(id)


def do_request():
    data = _get_req_data(request)
    service = data.get("service")
    action = data.get("action")
    if action == "balance":
        return services.get_balance(service)
    return services.call(service, action, omit(["service", "action"], data))


def dispatch_action(id, action):
    return compose(partial(services.call, id, action), _get_req_data)(request)


def _get_req_data(req):
    if req.content_type == "application/x-www-form-urlencoded":
        return req.form
    if req.content_type == "application/json":
        return req.get_json()
    raise UnsupportedContent(
        "Content-Type '{}' is not supported".format(req.content_type)
    )
