# -*- coding: utf-8 -*-

import graphene
from graphene import AbstractType, ObjectType, relay
from graphene_gae import NdbObjectType, NdbConnectionField

from messaging.models.services import (
    Service as ServiceModel,
    create,
    update,
    put_static,
)
from messaging.models.messages import Message as MessageModel
from messaging.schema.messages import Message as MessageType
from messaging.utils import pick
from messaging.helpers import ParamLocation, get_key
from messaging.exceptions import ExecutionUnauthorized


class ServiceStaticAbstract(AbstractType):
    field = graphene.String(required=True)
    value = graphene.String(required=True)
    location = ParamLocation(required=True)


class ServiceStatic(ObjectType, ServiceStaticAbstract):
    pass


class Service(NdbObjectType):
    class Meta:
        model = ServiceModel
        exclude_fields = ("vendor_key",)
        interfaces = (relay.Node,)

    statics = graphene.List(ServiceStatic)

    def resolve_statics(self, info, **args):
        return self.statics

    messages = NdbConnectionField(MessageType)

    def resolve_messages(self, info, **args):
        return MessageModel.query(ancestor=self.key)


class CreateService(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        account = graphene.String(required=True)
        provider = graphene.String(required=True)
        quota = graphene.Int()

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


class UpdateService(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String()
        provider = graphene.String()
        quota = graphene.Int()

    service = graphene.Field(Service)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        def check_and_get_provider():
            if not input.get("provider"):
                return None
            provider_key = get_key(input.get("provider"))
            if provider_key.parent() != info.context.user_key:
                raise ExecutionUnauthorized
            return provider_key

        service_key = get_key(input.get("id"))
        if service_key.parent().parent() != info.context.user_key:
            raise ExecutionUnauthorized

        service = update(
            fields=filter(lambda x: x != "id", cls.Input._meta.fields.keys()),
            service=service_key,
            provider=check_and_get_provider(),
            body=pick(["name", "quota"], input),
            as_obj=True,
        )
        return UpdateService(service=service)


class UpdateServiceStatic(relay.ClientIDMutation):
    class Input(ServiceStaticAbstract):
        id = graphene.ID(required=True)

    service = graphene.Field(Service)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        service_key = get_key(input.get("id"))
        if service_key.parent().parent() != info.context.user_key:
            raise ExecutionUnauthorized

        body = pick(["field", "value", "location"], input)
        service = put_static(service_key, body)
        return UpdateServiceStatic(service=service)
