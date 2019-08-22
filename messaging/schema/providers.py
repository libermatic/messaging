# -*- coding: utf-8 -*-

import graphene
from graphene import relay
from graphene_gae import NdbObjectType, NdbConnectionField

from messaging.models.providers import Provider as ProviderModel, create
from messaging.models.services import Service as ServiceModel
from messaging.schema.services import Service as ServiceType
from messaging.exceptions import ExecutionUnauthorized


class Provider(NdbObjectType):
    class Meta:
        model = ProviderModel
        interfaces = (relay.Node,)

    services = NdbConnectionField(ServiceType)

    def resolve_services(self, info, **args):
        return ServiceModel.query().filter(ServiceModel.provider == self.key)

    @classmethod
    def providers_resolver(cls, root, info):
        if not info.context.user_key:
            raise ExecutionUnauthorized()
        return ProviderModel.query(ancestor=info.context.user_key)


class CreateProvider(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        type = graphene.String()
        base_url = graphene.String(required=True)

    provider = graphene.Field(Provider)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        if not info.context.user_key:
            raise ExecutionUnauthorized()
        provider = create(
            fields=cls.Input._meta.fields.keys(),
            user=info.context.user_key,
            body=input,
            as_obj=True,
        )
        return CreateProvider(provider=provider)
