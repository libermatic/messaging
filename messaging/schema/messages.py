# -*- coding: utf-8 -*-

import graphene
from graphene import ObjectType, relay
from graphene_gae import NdbObjectType

from messaging.models.messages import Message as MessageModel


class MessageResponse(ObjectType):
    status_code = graphene.String()
    content = graphene.String()


class Message(NdbObjectType):
    class Meta:
        model = MessageModel
        interfaces = (relay.Node,)

    response = graphene.Field(MessageResponse)

    def resolve_response(self, info, **args):
        return MessageResponse(**self.response)
