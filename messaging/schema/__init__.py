# -*- coding: utf-8 -*-

import graphene
from graphene_gae import NdbConnectionField


from messaging.schema.accounts import Account as AccountType, CreateAccount
from messaging.schema.providers import Provider as ProviderType, CreateProvider
from messaging.schema.services import Service as ServiceType, CreateService
from messaging.schema.messages import Message as MessageType


class Query(graphene.ObjectType):
    messages = NdbConnectionField(MessageType)
    services = NdbConnectionField(ServiceType)
    providers = NdbConnectionField(ProviderType)
    accounts = NdbConnectionField(AccountType)


class Mutation(graphene.ObjectType):
    createAccount = CreateAccount.Field()
    createProvider = CreateProvider.Field()
    createService = CreateService.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
