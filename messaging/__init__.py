from flask import Flask
from flask_restful import Api

from messaging.resources.accounts import Account, AccountList, AccountKey


app = Flask(__name__)
api = Api(app)

api.add_resource(Account, '/accounts/<string:id>')
api.add_resource(AccountList, '/accounts')
api.add_resource(AccountKey, '/accounts/<string:id>/key')
