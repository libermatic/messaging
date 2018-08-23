# -*- coding: utf-8 -*-


class MessagingException(Exception):
    '''Base exception'''


class EntityAlreadyExists(MessagingException):
    '''Raises when entity already exists in store'''


class EntityNotFound(MessagingException):
    '''Raises when entity does not exists in store'''


class ReferencedEntityNotFound(EntityNotFound):
    '''Raises when a referenced entity is not found in store'''


class InvalidField(MessagingException):
    '''Raises when fields are of wrong type'''


class ServiceUnauthorized(MessagingException):
    '''Raises when access to service is unathorized'''


class ServiceMethodNotFound(MessagingException):
    '''Raises when a service does not have a method'''


class ServiceCallFailure(MessagingException):
    '''Raises when a call to service fails'''


class UnsupportedContent(MessagingException):
    '''Raises when the request content_type is not supported'''


errors = {
    'EntityAlreadyExists': {
        'message': "Entity already exists.",
        'status': 409,
    },
    'EntityNotFound': {
        'message': "Entity does not exists.",
        'status': 404,
    },
    'ReferencedEntityNotFound': {
        'message': "Referenced entity does not exists.",
        'status': 404,
    },
    'BadRequestError': {
        'message': "Missing required fields.",
        'status': 400,
    },
    'InvalidField': {
        'message': "Invalid datatype.",
        'status': 400,
    },
    'ServiceUnauthorized': {
        'message': "Unauthorized.",
        'status': 401,
    },
    'ServiceMethodNotFound': {
        'message': "Unsupported action.",
        'status': 400,
    },
    'ServiceCallFailure': {
        'message': "Unable to execute at this time.",
        'status': 503,
    },
    'UnsupportedContent': {
        'message': "Content Type is unsupported",
        'status': 400,
    }
}
