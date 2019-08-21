# -*- coding: utf-8 -*-

import graphene
from graphene import relay
from graphene_gae import NdbObjectType, NdbConnectionField

from messaging.models.accounts import Account as AccountModel
from messaging.models.services import Service as ServiceModel
from messaging.models.messages import Message as MessageModel
from messaging.schema.services import Service as ServiceType
from messaging.schema.messages import Message as MessageType
from messaging import helpers


class Account(NdbObjectType):
    class Meta:
        model = AccountModel
        exclude_fields = ("key_hash",)
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
        name = graphene.String(required=True)

    account = graphene.Field(Account)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        account = helpers.make_create(
            AccountModel, cls.Input._meta.fields.keys(), "site"
        )(input, as_obj=True)
        return CreateAccount(account=account)
