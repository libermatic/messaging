# -*- coding: utf-8 -*-

import graphene
from graphene_gae import NdbConnectionField
from graphene import relay


from messaging.schema.auth import User as UserType, SignUp, Logout
from messaging.schema.accounts import (
    Account as AccountType,
    CreateAccount,
    UpdateAccount,
    CreateAccountKey,
)
from messaging.schema.providers import (
    Provider as ProviderType,
    CreateProvider,
    UpdateProvider,
    DeleteProvider,
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
    DeleteServiceStatic,
    ResetBalance,
    LoadBalance,
)


class Query(graphene.ObjectType):
    node = relay.Node.Field()

    me = graphene.Field(UserType, resolver=UserType.me_resolver)

    accounts = NdbConnectionField(AccountType)
    resolve_accounts = AccountType.accounts_resolver

    providers = NdbConnectionField(ProviderType)
    resolve_providers = ProviderType.providers_resolver

    services = NdbConnectionField(ServiceType)
    resolve_services = ServiceType.services_resolver


class Mutation(graphene.ObjectType):
    signUp = SignUp.Field()
    logout = Logout.Field()

    createAccount = CreateAccount.Field()
    createAccountKey = CreateAccountKey.Field()
    updateAccount = UpdateAccount.Field()

    createProvider = CreateProvider.Field()
    updateProvider = UpdateProvider.Field()
    deleteProvider = DeleteProvider.Field()
    updateProviderMethod = UpdateProviderMethod.Field()
    deleteProviderMethod = DeleteProviderMethod.Field()
    updateProviderConfig = UpdateProviderConfig.Field()

    createService = CreateService.Field()
    updateService = UpdateService.Field()
    deleteService = DeleteService.Field()
    updateServiceStatic = UpdateServiceStatic.Field()
    deleteServiceStatic = DeleteServiceStatic.Field()
    resetBalance = ResetBalance.Field()
    loadBalance = LoadBalance.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
