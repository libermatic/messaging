# -*- coding: utf-8 -*-

import os
from flask_restful import Api
from flask import Flask, jsonify
from flask_graphql import GraphQLView
from flask_jwt_extended import JWTManager, jwt_required
from google.appengine.ext import ndb

from messaging.schema.auth import auth_middleware
from messaging.resources.auth import login
from messaging.resources.accounts import Account, AccountList, AccountKey
from messaging.resources.providers import (
    Provider,
    ProviderList,
    ProviderMethod,
    ProviderMethodPut,
    ProviderConfigPut,
)
from messaging.resources.services import (
    Service,
    ServiceList,
    ServiceAll,
    ServiceStaticPut,
    ServiceStatic,
    ServiceAction,
    ServiceBalance,
    get_balance,
    dispatch_action,
)
from messaging.resources.messages import MessageList, MessageAll
from messaging.exceptions import errors
from messaging.schema import schema
from messaging.exceptions import (
    ServiceUnauthorized,
    ServiceMethodNotFound,
    ServiceBalanceDepleted,
    UnsupportedContent,
    EntityNotFound,
    ServiceCallFailure,
    InvalidField,
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


api = Api(app, errors=errors)

api.add_resource(AccountList, "/accounts")
api.add_resource(Account, "/accounts/<string:id>")
api.add_resource(AccountKey, "/accounts/<string:id>/key")
api.add_resource(ProviderList, "/providers")
api.add_resource(Provider, "/providers/<string:id>")
api.add_resource(ProviderMethodPut, "/providers/<string:id>/methods")
api.add_resource(ProviderMethod, "/providers/<string:id>/methods/<string:action>")
api.add_resource(ProviderConfigPut, "/providers/<string:id>/config")
api.add_resource(ServiceList, "/accounts/<string:site>/services")
api.add_resource(ServiceAll, "/services")
api.add_resource(Service, "/services/<string:id>")
api.add_resource(ServiceStaticPut, "/services/<string:id>/static")
api.add_resource(ServiceStatic, "/services/<string:id>/static/<string:field>")
api.add_resource(ServiceBalance, "/services/<string:id>/balance")
api.add_resource(MessageList, "/services/<string:service>/messages")
api.add_resource(ServiceAction, "/services/<string:id>/<string:action>")
api.add_resource(MessageAll, "/messages")


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
def handle_rest_errors(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
