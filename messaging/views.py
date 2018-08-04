# -*- coding: utf-8 -*-

import os
from flask import request, jsonify, abort
from google.appengine.api.datastore_errors import (
    BadValueError, BadRequestError
)
import logging
from functools import partial
from toolz import compose

from messaging import app, accounts


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
def handle_accounts_key(id):
    try:
        return compose(jsonify, accounts.generate_api_key)(id)
    except ReferenceError:
        return abort(404, 'Entity not found')
            return abort(400, 'Entity already exists')
    return abort(400, 'WTF')


@app.route('/')
def index():
    return os.getenv('CURRENT_VERSION_ID', 'None').split('.')[0]


@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_4xx_errors(error):
    logging.exception(error)
    return jsonify({'error': error.description}), error.code
