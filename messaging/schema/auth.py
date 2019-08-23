# -*- coding: utf-8 -*-

from werkzeug.security import generate_password_hash, check_password_hash
import graphene
from graphene import relay
from graphene_gae import NdbObjectType, NdbConnectionField
from flask_jwt_extended import create_access_token, get_current_user
from toolz import merge

from messaging.models.user import User as UserModel
from messaging.models.accounts import Account as AccountModel
from messaging.models.providers import Provider as ProviderModel
from messaging.schema.accounts import Account as AccountType
from messaging.schema.providers import Provider as ProviderType
from messaging import helpers
from messaging.utils import pick
from messaging.exceptions import InvalidCredential


class User(NdbObjectType):
    class Meta:
        model = UserModel
        exclude_fields = UserModel._excluded_keys
        interfaces = (relay.Node,)

    @classmethod
    def me_resolver(cls, root, info):
        return info.context.user_key.get()

    accounts = NdbConnectionField(AccountType)

    def resolve_accounts(self, info, **args):
        return AccountModel.query(ancestor=self.key)

    providers = NdbConnectionField(ProviderType)

    def resolve_providers(self, info, **args):
        return ProviderModel.query(ancestor=self.key)


class SignUp(relay.ClientIDMutation):
    class Input:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        name = graphene.String()

    user = graphene.Field(User)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        fields = merge(
            pick(["email", "name"], input),
            {
                "password_hash": generate_password_hash(
                    input.get("password"), method="sha256"
                )
            },
        )
        user = helpers.make_create(
            UserModel, ["email", "name", "password_hash"], "email"
        )(fields, as_obj=True)
        return SignUp(user=user)


class Login(relay.ClientIDMutation):
    class Input:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    access_token = graphene.String()

    @classmethod
    def mutate_and_get_payload(cls, root, info, email, password):
        user = UserModel.get_by_id(email)
        if not user or not check_password_hash(user.password_hash, password):
            raise InvalidCredential("Account")
        access_token = create_access_token(identity=user.key.urlsafe())
        return Login(access_token=access_token)


class Logout(relay.ClientIDMutation):
    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        return Logout()


def do_login(request):
    data = request.get_json()
    user = UserModel.get_by_id(data.get("email"))
    if not user or not check_password_hash(user.password_hash, data.get("password")):
        raise InvalidCredential("Account")
    access_token = create_access_token(identity=user.key.urlsafe())
    return access_token


def auth_middleware(next, root, info, **args):
    info.context.user_key = get_current_user()
    return next(root, info, **args)
