# -*- coding: utf-8 -*-

import os
from flask import Flask, jsonify

from flask_graphql import GraphQLView
from flask_jwt_extended import JWTManager, jwt_required
from google.appengine.ext import ndb

from messaging.schema.auth import auth_middleware
from messaging.resources.auth import sign_up, login
from messaging.resources.services import get_balance, dispatch_action
from messaging.schema import schema
from messaging.exceptions import (
    ServiceUnauthorized,
    ServiceMethodNotFound,
    ServiceBalanceDepleted,
    UnsupportedContent,
    EntityNotFound,
    ServiceCallFailure,
    InvalidField,
    InvalidCredential,
)


import requests_toolbelt.adapters.appengine

requests_toolbelt.adapters.appengine.monkeypatch()

env = (
    "prod"
    if os.getenv("SERVER_SOFTWARE", "").startswith("Google App Engine/")
    else "dev"
)


app = Flask(__name__)
app.config.from_object("settings.{env}.FlaskConfig".format(env=env))

jwt = JWTManager(app)


@jwt.user_loader_callback_loader
def load_user(uid):
    return ndb.Key(urlsafe=uid)


app.add_url_rule("/sign-up", view_func=sign_up, methods=["POST"])
app.add_url_rule("/login", view_func=login, methods=["POST"])
app.add_url_rule(
    "/services/<string:id>/balance", view_func=get_balance, methods=["GET"]
)
app.add_url_rule(
    "/services/<string:id>/<string:action>", view_func=dispatch_action, methods=["POST"]
)
app.add_url_rule(
    "/graf",
    view_func=jwt_required(
        GraphQLView.as_view("graf", schema=schema, middleware=[auth_middleware])
    ),
)


@app.errorhandler(ServiceUnauthorized)
@app.errorhandler(ServiceMethodNotFound)
@app.errorhandler(ServiceBalanceDepleted)
@app.errorhandler(UnsupportedContent)
@app.errorhandler(EntityNotFound)
@app.errorhandler(ServiceCallFailure)
@app.errorhandler(InvalidField)
@app.errorhandler(InvalidCredential)
def handle_rest_errors(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
