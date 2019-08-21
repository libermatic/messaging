# -*- coding: utf-8 -*-

import graphene
from graphene import relay
from graphene_gae import NdbObjectType, NdbConnectionField

from messaging.models.providers import Provider as ProviderModel
from messaging.models.services import Service as ServiceModel
from messaging.schema.services import Service as ServiceType
from messaging import helpers


class Provider(NdbObjectType):
    class Meta:
        model = ProviderModel
        interfaces = (relay.Node,)

    services = NdbConnectionField(ServiceType)

    def resolve_services(self, info, **args):
        return ServiceModel.query().filter(ServiceModel.provider == self.key)


class CreateProvider(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        type = graphene.String()
        base_url = graphene.String(required=True)

    provider = graphene.Field(Provider)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        provider = helpers.make_create(
            ProviderModel, cls.Input._meta.fields.keys(), "name"
        )(input, as_obj=True)
        return CreateProvider(provider=provider)
