# -*- coding: utf-8 -*-

import graphene
from graphene import AbstractType, ObjectType, relay
from graphene_gae import NdbObjectType, NdbConnectionField

from messaging.models.providers import (
    Provider as ProviderModel,
    create,
    update,
    put_method,
    remove_method,
    put_config,
)
from messaging.models.services import Service as ServiceModel
from messaging.schema.services import Service as ServiceType
from messaging.utils import pick
from messaging.helpers import ParamLocation, get_key
from messaging.exceptions import ExecutionUnauthorized


class Method(graphene.Enum):
    GET = "GET"
    POST = "POST"


class ProviderMethodAbstract(AbstractType):
    action = graphene.String(required=True)
    method = Method(required=True)
    path = graphene.String(required=True)
    args = graphene.List(graphene.String)


class ProviderMethod(ObjectType, ProviderMethodAbstract):
    pass


class ProviderConfigAbstract(AbstractType):
    auth_field = graphene.String(required=True)
    auth_location = ParamLocation(required=True)
    error_field = graphene.String()
    error_condition = graphene.String()
    cost_field = graphene.String()
    balance_field = graphene.String()


class ProviderConfig(ObjectType, ProviderConfigAbstract):
    pass


class Provider(NdbObjectType):
    class Meta:
        model = ProviderModel
        interfaces = (relay.Node,)

    methods = graphene.List(ProviderMethod)

    def resolve_methods(self, info, **args):
        return map(lambda x: ProviderMethod(**x), self.methods.values())

    config = graphene.Field(ProviderConfig)

    def resolve_config(self, info, **args):
        return ProviderConfig(**self.config)

    services = NdbConnectionField(ServiceType)

    def resolve_services(self, info, **args):
        return ServiceModel.query().filter(ServiceModel.provider == self.key)

    @classmethod
    def providers_resolver(cls, root, info):
        return ProviderModel.query(ancestor=info.context.user_key)


class ProviderType(graphene.Enum):
    TEXT = "text"


class CreateProvider(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        type = ProviderType()
        base_url = graphene.String(required=True)

    provider = graphene.Field(Provider)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        provider = create(
            fields=cls.Input._meta.fields.keys(),
            user=info.context.user_key,
            body=input,
            as_obj=True,
        )
        return CreateProvider(provider=provider)


class UpdateProvider(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String()
        type = graphene.String()
        base_url = graphene.String()

    provider = graphene.Field(Provider)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        provider_key = get_key(input.get("id"))
        if provider_key.parent() != info.context.user_key:
            raise ExecutionUnauthorized
        provider = update(
            fields=filter(lambda x: x != "id", cls.Input._meta.fields.keys()),
            provider=provider_key,
            body=pick(["name", "type", "base_url"], input),
            as_obj=True,
        )
        return UpdateProvider(provider=provider)


class UpdateProviderMethod(relay.ClientIDMutation):
    class Input(ProviderMethodAbstract):
        id = graphene.ID(required=True)

    provider = graphene.Field(Provider)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        provider_key = get_key(input.get("id"))
        if provider_key.parent() != info.context.user_key:
            raise ExecutionUnauthorized
        body = pick(["action", "method", "path", "args"], input)
        provider = put_method(provider_key, body)
        return UpdateProviderMethod(provider=provider)


class DeleteProviderMethod(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        action = graphene.String(required=True)

    provider = graphene.Field(Provider)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        provider_key = get_key(input.get("id"))
        if provider_key.parent() != info.context.user_key:
            raise ExecutionUnauthorized
        provider = remove_method(provider_key, input.get("action"))
        return UpdateProviderMethod(provider=provider)


class UpdateProviderConfig(relay.ClientIDMutation):
    class Input(ProviderConfigAbstract):
        id = graphene.ID(required=True)

    provider = graphene.Field(Provider)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        provider_key = get_key(input.get("id"))
        if provider_key.parent() != info.context.user_key:
            raise ExecutionUnauthorized
        body = pick(
            [
                "auth_field",
                "auth_location",
                "error_field",
                "error_condition",
                "cost_field",
                "balance_field",
            ],
            input,
        )
        provider = put_config(provider_key, body)
        return UpdateProviderConfig(provider=provider)
