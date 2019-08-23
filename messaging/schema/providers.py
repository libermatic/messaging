# -*- coding: utf-8 -*-

import graphene
from graphene import ObjectType, relay
from graphene_gae import NdbObjectType, NdbConnectionField

from messaging.models.providers import (
    Provider as ProviderModel,
    create,
    put_method,
    remove_method,
)
from messaging.models.services import Service as ServiceModel
from messaging.schema.services import Service as ServiceType
from messaging.utils import pick
from messaging.helpers import get_key
from messaging.exceptions import ExecutionUnauthorized


class ProviderMethod(ObjectType):
    action = graphene.String(required=True)
    method = graphene.String(required=True)
    path = graphene.String(required=True)
    args = graphene.List(graphene.String)


class Provider(NdbObjectType):
    class Meta:
        model = ProviderModel
        interfaces = (relay.Node,)

    methods = graphene.List(ProviderMethod)

    def resolve_methods(self, info, **args):
        return map(lambda x: ProviderMethod(**x), self.methods.values())

    services = NdbConnectionField(ServiceType)

    def resolve_services(self, info, **args):
        return ServiceModel.query().filter(ServiceModel.provider == self.key)

    @classmethod
    def providers_resolver(cls, root, info):
        return ProviderModel.query(ancestor=info.context.user_key)


class CreateProvider(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        type = graphene.String()
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


class UpdateProviderMethod(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        action = graphene.String(required=True)
        method = graphene.String(required=True, choices=["GET", "POST"])
        path = graphene.String(required=True)
        args = graphene.List(graphene.String)

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
