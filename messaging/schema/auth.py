# -*- coding: utf-8 -*-

from werkzeug.security import check_password_hash
import graphene
from graphene import relay
from flask_jwt_extended import create_access_token

from messaging.models.accounts import Account as AccountModel
from messaging.exceptions import InvalidCredential


class _Indentity:
    def __init__(self, uid, site=None):
        self.uid = uid
        self.site = site


class Login(relay.ClientIDMutation):
    class Input:
        site = graphene.String(required=True)
        password = graphene.String(required=True)

    access_token = graphene.String()

    @classmethod
    def mutate_and_get_payload(cls, root, info, site, password):
        account = AccountModel.get_by_id(site)
        if not account or not check_password_hash(account.password_hash, password):
            raise InvalidCredential("Account")
        identity = _Indentity(uid=account.key.urlsafe(), site=site)
        access_token = create_access_token(identity=identity)
        return Login(access_token=access_token)
