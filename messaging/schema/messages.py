# -*- coding: utf-8 -*-

from graphene import relay
from graphene_gae import NdbObjectType

from messaging.models.messages import Message as MessageModel


class Message(NdbObjectType):
    class Meta:
        model = MessageModel
        exclude_fields = ("vendor_key",)
        interfaces = (relay.Node,)
