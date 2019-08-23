# -*- coding: utf-8 -*-

import graphene
from graphene import AbstractType, relay
from graphene_gae import NdbObjectType, NdbConnectionField

from messaging.models.services import Service as ServiceModel, create
from messaging.models.messages import Message as MessageModel
from messaging.schema.messages import Message as MessageType
from messaging.utils import pick
from messaging.helpers import get_key
from messaging.exceptions import ExecutionUnauthorized


class Service(NdbObjectType):
    class Meta:
        model = ServiceModel
        exclude_fields = ("vendor_key",)
        interfaces = (relay.Node,)

    messages = NdbConnectionField(MessageType)

    def resolve_messages(self, info, **args):
        return MessageModel.query(ancestor=self.key)


class ServiceInput(AbstractType):
    name = graphene.String(required=True)
    provider = graphene.String(required=True)
    quota = graphene.Int()


class CreateService(relay.ClientIDMutation):
    class Input(ServiceInput):
        account = graphene.String(required=True)

    service = graphene.Field(Service)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        account_key = get_key(input.get("account"))
        provider_key = get_key(input.get("provider"))
        if (
            account_key.parent() != info.context.user_key
            or provider_key.parent() != info.context.user_key
        ):
            raise ExecutionUnauthorized

        service = create(
            fields=filter(lambda x: x != "account", cls.Input._meta.fields.keys()),
            account=account_key,
            provider=provider_key,
            body=pick(["name", "quota"], input),
            as_obj=True,
        )
        return CreateService(service=service)
