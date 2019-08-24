# -*- coding: utf-8 -*-
from graphql import GraphQLError


class ExecutionUnauthorized(GraphQLError):
    """
        Raises when the operation requires authorization and none is found in the
        context
    """

    def __init__(self, message=None, **args):
        super(ExecutionUnauthorized, self).__init__(
            message or "Unauthorized execution", **args
        )


class InvalidCredential(GraphQLError):
    """Raises site and password does not match"""

    def __init__(self, message=None, **args):
        super(InvalidCredential, self).__init__(
            message or "Invalid credentials", **args
        )


class EntityAlreadyExists(GraphQLError):
    """Raises when entity already exists in store"""

    def __init__(self, entity, message=None, **args):
        super(EntityAlreadyExists, self).__init__(
            message or "Entity already exists for {}".format(entity), **args
        )


class EntityNotFound(GraphQLError):
    """Raises when entity does not exists in store"""

    def __init__(self, entity, message=None, **args):
        super(EntityNotFound, self).__init__(
            message or "Entity not found for {}".format(entity), **args
        )


class ReferencedEntityNotFound(GraphQLError):
    """Raises when a referenced entity is not found in store"""

    def __init__(self, entity, message=None, **args):
        super(ReferencedEntityNotFound, self).__init__(
            message or "Reference not found for to Entity {}".format(entity), **args
        )


class MessagingException(Exception):
    """Base exception"""


class InvalidField(MessagingException):
    """Raises when fields are of wrong type"""


class ServiceUnauthorized(MessagingException):
    """Raises when access to service is unathorized"""

    def __init__(self, message=None, **args):
        super(ServiceUnauthorized, self).__init__(
            message or "Unauthorized service", **args
        )


class ServiceMethodNotFound(MessagingException):
    """Raises when a service does not have a method"""

    def __init__(self, message=None, **args):
        super(ServiceMethodNotFound, self).__init__(
            message or "Unsupported or invalid method", **args
        )


class ServiceCallFailure(MessagingException):
    """Raises when a call to service fails"""


class UnsupportedContent(MessagingException):
    """Raises when the request content_type is not supported"""


class ServiceBalanceDepleted(MessagingException):
    """Raises trying to call service without balance"""


errors = {
    "EntityAlreadyExists": {"message": "Entity already exists.", "status": 409},
    "EntityNotFound": {"message": "Entity does not exists.", "status": 404},
    "ReferencedEntityNotFound": {
        "message": "Referenced entity does not exists.",
        "status": 404,
    },
    "BadRequestError": {"message": "Missing required fields.", "status": 400},
    "InvalidField": {"message": "Invalid datatype.", "status": 400},
    "ServiceUnauthorized": {"message": "Unauthorized.", "status": 401},
    "ServiceMethodNotFound": {"message": "Unsupported action.", "status": 400},
    "ServiceCallFailure": {"message": "Unable to execute at this time.", "status": 503},
    "UnsupportedContent": {"message": "Content Type is unsupported", "status": 400},
    "ServiceBalanceDepleted": {"message": "Balance exhausted", "status": 402},
}
