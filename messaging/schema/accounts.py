# -*- coding: utf-8 -*-

from werkzeug.security import generate_password_hash
from google.appengine.ext import ndb
import graphene
from graphene import relay
from graphene_gae import NdbObjectType, NdbConnectionField
from functools import partial
from toolz import compose, get, merge

from messaging.models.accounts import Account as AccountModel, generate_api_key
from messaging.models.services import Service as ServiceModel
from messaging.models.messages import Message as MessageModel
from messaging.schema.services import Service as ServiceType
from messaging.schema.messages import Message as MessageType
from messaging import helpers
from messaging.utils import pick


class Account(NdbObjectType):
    class Meta:
        model = AccountModel
        exclude_fields = AccountModel._excluded_keys
        interfaces = (relay.Node,)

    services = NdbConnectionField(ServiceType)

    def resolve_services(self, info, **args):
        return ServiceModel.query(ancestor=self.key)

    messages = NdbConnectionField(MessageType)

    def resolve_messages(self, info, **args):
        return MessageModel.query(ancestor=self.key)


class CreateAccount(relay.ClientIDMutation):
    class Input:
        site = graphene.String(required=True)
        password = graphene.String(required=True)
        name = graphene.String(required=True)

    account = graphene.Field(Account)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        fields = merge(
            pick(["site", "name"], input),
            {
                "password_hash": generate_password_hash(
                    input.get("password"), method="sha256"
                )
            },
        )
        account = helpers.make_create(
            AccountModel, ["site", "name", "password_hash"], "site"
        )(fields, as_obj=True)
        return CreateAccount(account=account)


class CreateAccountKey(relay.ClientIDMutation):
    class Input:
        id = graphene.String(required=True)

    key = graphene.String()

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        get_key = compose(
            generate_api_key,
            lambda x: ndb.Key(urlsafe=x).id(),
            lambda x: x[1],
            relay.Node.from_global_id,
            partial(get, "id"),
        )
        return CreateAccountKey(key=get_key(input))
