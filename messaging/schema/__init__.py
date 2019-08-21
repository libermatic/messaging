# -*- coding: utf-8 -*-

import graphene
from graphene_gae import NdbConnectionField
from graphene import relay


from messaging.schema.accounts import (
    Account as AccountType,
    CreateAccount,
    CreateAccountKey,
)
from messaging.schema.providers import Provider as ProviderType, CreateProvider
from messaging.schema.services import Service as ServiceType, CreateService
from messaging.schema.messages import Message as MessageType


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    messages = NdbConnectionField(MessageType)
    services = NdbConnectionField(ServiceType)
    providers = NdbConnectionField(ProviderType)
    accounts = NdbConnectionField(AccountType)


class Mutation(graphene.ObjectType):
    createAccount = CreateAccount.Field()
    createAccountKey = CreateAccountKey.Field()
    createProvider = CreateProvider.Field()
    createService = CreateService.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
