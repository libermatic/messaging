# -*- coding: utf-8 -*-

import os
from flask import request, jsonify, abort
from google.appengine.api.datastore_errors import (
    BadValueError, BadRequestError
)
import logging
from functools import partial
from toolz import compose
from werkzeug.exceptions import HTTPException

from messaging import app, accounts, providers, services, messages


@app.route('/accounts', methods=['GET', 'POST'])
@app.route('/accounts/<id>', methods=['GET', 'PUT', 'DELETE'])
def handle_accounts(id=None):
    if id:
        try:
            if request.method == 'GET':
                return compose(jsonify, accounts.get)(id)
            if request.method == 'PUT':
                return compose(
                    jsonify, partial(accounts.update, id), request.get_json
                )()
            if request.method == 'DELETE':
                return compose(jsonify, accounts.delete)(id), 204
        except ReferenceError:
            return abort(404, 'Entity not found')
    if request.method == 'GET':
        return compose(jsonify, accounts.list)()
    if request.method == 'POST':
        try:
            return compose(jsonify, accounts.create, request.get_json)()
        except (BadValueError, BadRequestError):
            return abort(400, 'Invalid datatype or missing required fields')
        except ReferenceError:
            return abort(400, 'Entity already exists')
    return abort(400, 'WTF')


@app.route('/accounts/<id>/key')
def handle_key_gen(id):
    try:
        return compose(jsonify, accounts.generate_api_key)(id)
    except ReferenceError:
        return abort(404, 'Entity not found')


@app.route('/providers', methods=['GET', 'POST'])
@app.route('/providers/<id>', methods=['GET', 'PUT', 'DELETE'])
def handle_providers(id=None):
    if id:
        try:
            if request.method == 'GET':
                return compose(jsonify, providers.get)(id)
            if request.method == 'PUT':
                return compose(
                    jsonify, partial(providers.update, id), request.get_json
                )()
            if request.method == 'DELETE':
                return compose(jsonify, providers.delete)(id), 204
        except ReferenceError:
            return abort(404, 'Entity not found')
    if request.method == 'GET':
        return compose(jsonify, providers.list)()
    if request.method == 'POST':
        try:
            return compose(jsonify, providers.create, request.get_json)()
        except (BadValueError, BadRequestError):
            return abort(400, 'Invalid datatype or missing required fields')
        except ReferenceError:
            return abort(400, 'Entity already exists')
    return abort(400, 'WTF')


@app.route('/accounts/<site>/services', methods=['GET', 'POST'])
def handle_accounts_services(site):
    if request.method == 'GET':
        return compose(jsonify, services.list)(site)
    if request.method == 'POST':
        try:
            return compose(
                jsonify,
                partial(services.create, site=site),
                request.get_json,
            )()
        except (BadValueError, BadRequestError):
            return abort(400, 'Invalid datatype or missing required fields')
        except ReferenceError:
            return abort(404, 'Referenced entity not found')


@app.route('/services/<id>', methods=['GET', 'PUT', 'DELETE'])
def handle_services(id):
    try:
        if request.method == 'GET':
            return compose(jsonify, services.get)(id)
        if request.method == 'PUT':
            return compose(
                jsonify, partial(services.update, id), request.get_json
            )()
        if request.method == 'DELETE':
            return compose(jsonify, services.delete)(id), 204
    except ReferenceError:
        return abort(404, 'Entity not found')


@app.route('/services/<id>/message', methods=['GET', 'POST'])
def handle_messages(id):
    def get_payload():
        if request.method == 'GET':
            return request.args
        if request.method == 'POST':
            return request.json if request.is_json else request.form
        return None

    try:
        return compose(
            jsonify,
            partial(messages.create, service_id=id),
            get_payload,
        )()
    except ReferenceError as e:
        if e.message == 'INVALID_USER':
            return abort(401, 'Invalid user')
        return abort(404, 'Entity not found')
    except ValueError:
        error = PaymentRequired(description='Balance depleted')
        return handle_4xx_errors(error)


@app.route('/')
def index():
    return os.getenv('CURRENT_VERSION_ID', 'None').split('.')[0]


class PaymentRequired(HTTPException):
    code = 402
    description = '<p>Payment required.</p>'


@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_4xx_errors(error):
    logging.exception(error)
    return jsonify({'error': error.description}), error.code
