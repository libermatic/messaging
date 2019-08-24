# -*- coding: utf-8 -*-
from graphql import GraphQLError


class RestException(Exception):
    """Base exception"""

    def __init__(self, message=None):
        super(RestException, self).__init__(message)
        if message:
            self.message = message

    def to_dict(self):
        return dict(status_code=self.status_code, message=self.message)


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


class EntityNotFound(GraphQLError, RestException):
    """Raises when entity does not exists in store"""

    status_code = 404

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


class ServiceUnauthorized(RestException):
    """Raises when access to service is unathorized"""

    status_code = 401
    message = "Unauthorized service"


class ServiceMethodNotFound(RestException):
    """Raises when a service does not have a method"""

    status_code = 404
    message = "Unsupported action"


class ServiceBalanceDepleted(RestException):
    """Raises trying to call service without balance"""

    status_code = 402
    message = "Balance exhausted"


class UnsupportedContent(RestException):
    """Raises when the request content_type is not supported"""

    status_code = 400
    message = "Content Type is unsupported"


class ServiceCallFailure(RestException):
    """Raises when a call to service fails"""

    status_code = 503
    message = "Unable to execute at this tim"


class InvalidField(RestException):
    """Raises when fields are of wrong type"""

    status_code = 400
    message = "Invalid datatype"


# errors = {
#     "EntityAlreadyExists": {"message": "Entity already exists.", "status": 409},
#     "EntityNotFound": {"message": "Entity does not exists.", "status": 404},
#     "ReferencedEntityNotFound": {
#         "message": "Referenced entity does not exists.",
#         "status": 404,
#     },
#     "BadRequestError": {"message": "Missing required fields.", "status": 400},
#     "InvalidField": {"message": "Invalid datatype.", "status": 400},
#     "ServiceUnauthorized": {"message": "Unauthorized.", "status": 401},
#     "ServiceMethodNotFound": {"message": "Unsupported action.", "status": 400},
#     "ServiceCallFailure": {"message": "Unable to execute at this time.", "status": 503},
#     "UnsupportedContent": {"message": "Content Type is unsupported", "status": 400},
#     "ServiceBalanceDepleted": {"message": "Balance exhausted", "status": 402},
# }
