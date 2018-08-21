from flask import Flask
from flask_restful import Api

from messaging.resources.accounts import Account, AccountList, AccountKey
from messaging.resources.providers \
    import Provider, ProviderList, ProviderMethod, ProviderMethodPut
from messaging.resources.services import Service, ServiceList, ServiceAll


app = Flask(__name__)
api = Api(app)

api.add_resource(AccountList, '/accounts')
api.add_resource(Account, '/accounts/<string:id>')
api.add_resource(AccountKey, '/accounts/<string:id>/key')
api.add_resource(ProviderList, '/providers')
api.add_resource(Provider, '/providers/<string:id>')
api.add_resource(
    ProviderMethod, '/providers/<string:id>/methods/<string:action>',
)
api.add_resource(ProviderMethodPut, '/providers/<string:id>/methods')
api.add_resource(ServiceList, '/accounts/<string:site>/services')
api.add_resource(ServiceAll, '/services')
api.add_resource(Service, '/services/<string:id>')
