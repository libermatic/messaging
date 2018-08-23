from flask import Flask
from flask_restful import Api

from messaging.resources.accounts import Account, AccountList, AccountKey
from messaging.resources.providers \
    import Provider, ProviderList, ProviderMethod, ProviderMethodPut, \
    ProviderConfigPut
from messaging.resources.services \
    import Service, ServiceList, ServiceAll, ServiceStaticPut, ServiceStatic, \
    ServiceAction
from messaging.resources.messages import MessageList, MessageAll
from messaging.exceptions import errors


import requests_toolbelt.adapters.appengine
requests_toolbelt.adapters.appengine.monkeypatch()


app = Flask(__name__)
api = Api(app, errors=errors)

api.add_resource(AccountList, '/accounts')
api.add_resource(Account, '/accounts/<string:id>')
api.add_resource(AccountKey, '/accounts/<string:id>/key')
api.add_resource(ProviderList, '/providers')
api.add_resource(Provider, '/providers/<string:id>')
api.add_resource(ProviderMethodPut, '/providers/<string:id>/methods')
api.add_resource(
    ProviderMethod, '/providers/<string:id>/methods/<string:action>',
)
api.add_resource(ProviderConfigPut, '/providers/<string:id>/config')
api.add_resource(ServiceList, '/accounts/<string:site>/services')
api.add_resource(ServiceAll, '/services')
api.add_resource(Service, '/services/<string:id>')
api.add_resource(ServiceStaticPut, '/services/<string:id>/static')
api.add_resource(ServiceStatic, '/services/<string:id>/static/<string:field>')
api.add_resource(MessageList, '/services/<string:service>/messages')
api.add_resource(ServiceAction, '/services/<string:id>/<string:action>')
api.add_resource(MessageAll, '/messages')
