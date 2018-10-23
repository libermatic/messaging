# -*- coding: utf-8 -*-

import graphene
from graphene import relay
from graphene_gae import NdbObjectType, NdbConnectionField
from toolz import dissoc

from messaging.models.services import Service as ServiceModel, create
from messaging.models.messages import Message as MessageModel
from messaging.schema.messages import Message as MessageType


class Service(NdbObjectType):
    class Meta:
        model = ServiceModel
        exclude_fields = ('vendor_key', )
        interfaces = (relay.Node, )

    messages = NdbConnectionField(MessageType)

    def resolve_messages(self, info, **args):
        return MessageModel.query(ancestor=self.key)


class CreateService(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        site = graphene.String(required=True)
        provider = graphene.String(required=True)
        quota = graphene.Int()

    service = graphene.Field(Service)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        fields = filter(lambda x: x != 'site', cls.Input._meta.fields.keys())
        service = create(
            fields=fields,
            site=input.get('site'),
            body=dissoc(input, 'site'),
            as_obj=True,
        )
        return CreateService(service=service)
