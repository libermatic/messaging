# -*- coding: utf-8 -*-

import graphene
from graphene_gae import NdbConnectionField
from graphene import relay


from messaging.schema.auth import User as UserType, SignUp, Logout
from messaging.schema.accounts import (
    Account as AccountType,
    CreateAccount,
    CreateAccountKey,
)
from messaging.schema.providers import (
    Provider as ProviderType,
    CreateProvider,
    UpdateProviderMethod,
    DeleteProviderMethod,
    UpdateProviderConfig,
)
from messaging.schema.services import (
    Service as ServiceType,
    CreateService,
    UpdateService,
    DeleteService,
    UpdateServiceStatic,
)
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
    logout = Logout.Field()
    createAccount = CreateAccount.Field()
    createAccountKey = CreateAccountKey.Field()
    createProvider = CreateProvider.Field()
    updateProviderMethod = UpdateProviderMethod.Field()
    deleteProviderMethod = DeleteProviderMethod.Field()
    updateProviderConfig = UpdateProviderConfig.Field()
    createService = CreateService.Field()
    updateService = UpdateService.Field()
    deleteService = DeleteService.Field()
    updateServiceStatic = UpdateServiceStatic.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
