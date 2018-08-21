from flask import Flask
from flask_restful import Api

from messaging.resources.accounts import Account, AccountList, AccountKey
from messaging.resources.providers \
    import Provider, ProviderList, ProviderMethod, ProviderMethodPut


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
