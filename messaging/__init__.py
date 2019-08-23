# -*- coding: utf-8 -*-

import os
from flask import Flask, request, jsonify, abort
from flask_restful import Api
from flask_graphql import GraphQLView
from flask_jwt_extended import JWTManager, jwt_optional
from google.appengine.ext import ndb

from messaging.schema.auth import auth_middleware, do_login
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
)
from messaging.resources.messages import MessageList, MessageAll
from messaging.exceptions import errors
from messaging.schema import schema


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

view_func = GraphQLView.as_view(
    "graphql", schema=schema, graphiql=False, middleware=[auth_middleware]

@app.route("/login", methods=["POST"])
def login():
    try:
        access_token = do_login(request)
        return jsonify({"access_token": access_token})
    except Exception as e:
        if type(e).__name__ == "InvalidCredential":
            abort(401)
        raise e
)

app.add_url_rule("/graphql", view_func=jwt_optional(view_func))
