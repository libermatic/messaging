# -*- coding: utf-8 -*-

import graphene
from graphene import relay
from graphene_gae import NdbObjectType, NdbConnectionField

from messaging.models.accounts import (
    Account as AccountModel,
    create,
    update,
    delete,
    generate_api_key,
)
from messaging.models.services import Service as ServiceModel
from messaging.models.messages import Message as MessageModel
from messaging.schema.services import Service as ServiceType
from messaging.schema.messages import Message as MessageType
from messaging.utils import pick
from messaging.helpers import get_key
from messaging.exceptions import ExecutionUnauthorized


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

    @classmethod
    def accounts_resolver(cls, root, info):
        return AccountModel.query(ancestor=info.context.user_key)


class CreateAccount(relay.ClientIDMutation):
    class Input:
        site = graphene.String(required=True)
        name = graphene.String(required=True)

    account = graphene.Field(Account)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        account = create(
            fields=cls.Input._meta.fields.keys(),
            user=info.context.user_key,
            body=input,
            as_obj=True,
        )
        return CreateAccount(account=account)


class UpdateAccount(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        site = graphene.String()
        name = graphene.String()

    account = graphene.Field(Account)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        account_key = get_key(input.get("id"))
        if account_key.parent() != info.context.user_key:
            raise ExecutionUnauthorized
        account = update(
            fields=filter(lambda x: x != "id", cls.Input._meta.fields.keys()),
            account=account_key,
            body=pick(["site", "name"], input),
            as_obj=True,
        )
        return UpdateAccount(account=account)


class DeleteAccount(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, id):
        account_key = get_key(input.get("id"))
        if account_key.parent() != info.context.user_key:
            raise ExecutionUnauthorized
        delete(account_key)
        return DeleteAccount()


class CreateAccountKey(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    key = graphene.String()

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        account_key = get_key(input.get("id"))
        if account_key.parent() != info.context.user_key:
            raise ExecutionUnauthorized
        key = generate_api_key(account_key)
        return CreateAccountKey(key=key)
