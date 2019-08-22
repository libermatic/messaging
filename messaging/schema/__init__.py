# -*- coding: utf-8 -*-

import graphene
from graphene_gae import NdbConnectionField
from graphene import relay


from messaging.schema.auth import User as UserType, SignUp, Login, Logout
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

    me = graphene.Field(UserType, resolver=UserType.me_resolver)

    accounts = NdbConnectionField(AccountType)
    resolve_accounts = AccountType.accounts_resolver

    providers = NdbConnectionField(ProviderType)
    resolve_providers = ProviderType.providers_resolver


class Mutation(graphene.ObjectType):
    signUp = SignUp.Field()
    login = Login.Field()
    logout = Logout.Field()
    createAccount = CreateAccount.Field()
    createAccountKey = CreateAccountKey.Field()
    createProvider = CreateProvider.Field()
    createService = CreateService.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
