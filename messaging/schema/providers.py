# -*- coding: utf-8 -*-

import graphene
from graphene import AbstractType, ObjectType, InputObjectType, relay
from graphene_gae import NdbObjectType, NdbConnectionField

from messaging.models.providers import (
    Provider as ProviderModel,
    create,
    update,
    delete,
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


class StringEncoderAbstract(AbstractType):
    plain = graphene.String(required=True)
    encoded = graphene.String(required=True)


class ProviderConfigAbstract(AbstractType):
    auth_field = graphene.String(required=True)
    auth_location = ParamLocation(required=True)
    error_field = graphene.String()
    error_condition = graphene.String()
    cost_field = graphene.String()
    balance_field = graphene.String()


class StringEncoder(ObjectType, StringEncoderAbstract):
    pass


class ProviderConfig(ObjectType, ProviderConfigAbstract):
    encoders = graphene.List(StringEncoder)


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


_provider_fields = ["name", "type", "base_url"]


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
            body=pick(_provider_fields, input),
            as_obj=True,
        )
        return UpdateProvider(provider=provider)


class DeleteProvider(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, id):
        provider_key = get_key(id)
        if provider_key.parent() != info.context.user_key:
            raise ExecutionUnauthorized
        delete(provider_key)
        return DeleteProvider()


_provider_method_fields = ["action", "method", "path", "args"]


class UpdateProviderMethod(relay.ClientIDMutation):
    class Input(ProviderMethodAbstract):
        id = graphene.ID(required=True)

    provider = graphene.Field(Provider)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        provider_key = get_key(input.get("id"))
        if provider_key.parent() != info.context.user_key:
            raise ExecutionUnauthorized
        body = pick(_provider_method_fields, input)
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


class StringEncoderInput(InputObjectType, StringEncoderAbstract):
    pass


_provider_config_fields = [
    "auth_field",
    "auth_location",
    "error_field",
    "error_condition",
    "cost_field",
    "balance_field",
    "encoders",
]


class UpdateProviderConfig(relay.ClientIDMutation):
    class Input(ProviderConfigAbstract):
        id = graphene.ID(required=True)
        auth_field = graphene.String()
        auth_location = ParamLocation()
        encoders = graphene.List(StringEncoderInput)

    provider = graphene.Field(Provider)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        provider_key = get_key(input.get("id"))
        if provider_key.parent() != info.context.user_key:
            raise ExecutionUnauthorized
        body = pick(_provider_config_fields, input)
        provider = put_config(provider_key, body)
        return UpdateProviderConfig(provider=provider)
