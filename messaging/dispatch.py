# -*- coding: utf-8 -*-

import requests
from functools import reduce, partial
from toolz import merge, assoc, valfilter

from messaging.utils import pick
from messaging.exceptions import ServiceCallFailure


def _make_url(method):
    return method.get("base_url") + method.get("path")


def _make_args(locations):
    def field_reduce(a, x):
        if x.get("location") in locations:
            return assoc(a, x.get("field"), x.get("value"))
        return a

    def fn(config, key, statics):
        auth = (
            {config.get("auth_label"): key}
            if config.get("auth_location") in locations
            else {}
        )
        others = reduce(field_reduce, statics, {})
        return merge(auth, others)

    return fn


def _make_condition_check(config):
    condition = config.get("error_condition")

    def fn(d):
        if not condition:
            return True
        return bool(eval(condition, {"__builtins__": None}, dict(d)))

    return fn


def _make_kv_check(config):
    k = config.get("error_field")
    v = config.get("error_value")

    def fn(d):
        if k and k in d:
            if not v:
                return True
            if v == d[k]:
                return True
        return False

    return fn


def _make_prices(config):
    def map_fields(to_d, from_d):
        return valfilter(
            lambda v: v is not None, {k: from_d.get(v) for k, v in to_d.iteritems()}
        )

    price_map = {"cost": "cost_field", "balance": "balance_field"}
    return partial(map_fields, map_fields(price_map, config))


def request(key, statics, config, method, body):
    make_headers = _make_args(["header"])
    make_payload = _make_args(["body", "query"])
    headers = make_headers(config, key, statics)
    payload = merge(pick(method.get("args"), body), make_payload(config, key, statics))
    kwargs = {
        "method": method.get("method"),
        "url": _make_url(method),
        "data" if method.get("method") == "POST" else "params": payload,
        "headers": headers,
    }

    try:
        res = requests.request(**kwargs)
        result = res.json()

        contains_error_condition = _make_condition_check(config)
        contains_error_field = _make_kv_check(config)
        has_failed = (
            not res.ok
            or contains_error_condition(result)
            or contains_error_field(result)
        )
        prices = _make_prices(config)

        return merge(
            {
                "status": "failure" if has_failed else "success",
                "response": {"status_code": res.status_code, "content": result},
            },
            prices(result) if not has_failed else {},
        )
    except (requests.ConnectionError, requests.Timeout) as e:
        raise ServiceCallFailure(*e)
