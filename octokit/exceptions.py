# -*- coding: utf-8 -*-

"""
octokit.exceptions
~~~~~~~~~~~~~~~~~~

This module contains octokit.py exceptions.
"""


class Error(Exception):
    """Something went wrong."""

    def __init__(self, data={'message': 'Something went wrong.'}):
        self.message = data['message']

    def __str__(self):
        return repr(self.message)


class ClientError(Error):
    """Status 4xx: Client error."""


class BadRequest(ClientError):
    """Status 400: Bad request."""


class Unauthorized(ClientError):
    """Status 401/403: Not authorized to view the resource"""


class NotFound(ClientError):
    """Status 404: The resource wasn't found."""

    def __init__(self, data={"message": "Not Found"}):
        super(NotFound, self).__init__(data)


class MethodNotAllowed(ClientError):
    """Status 405: The method is not allowed."""


class NotAcceptable(ClientError):
    """Status 406: The response is unacceptable."""


class Conflict(ClientError):
    """Status 409: Conflict with the current state of the resource."""


class UnsupportedMediaType(ClientError):
    """Status 415: Unsupported media type."""


class UnprocessableEntity(ClientError):
    """Status 422: Unprocessable entity."""


class ServerError(Error):
    """Status 5xx: Server error."""


class InternalServerError(ServerError):
    """Status 500: Internal server error."""


class NotImplemented(ServerError):
    """Status 501: Not implemented."""


class BadGateway(ServerError):
    """Status 502: Bad gateway."""


class ServiceUnavailable(ServerError):
    """Status 503: Service unavailable."""


# Mapping of status code to Exception
STATUS_ERRORS = {
  400: BadRequest,
  401: Unauthorized,
  403: Unauthorized,
  404: NotFound,
  405: MethodNotAllowed,
  406: NotAcceptable,
  409: Conflict,
  415: UnsupportedMediaType,
  422: UnprocessableEntity,
  499: ClientError,
  500: InternalServerError,
  501: NotImplemented,
  502: BadGateway,
  503: ServiceUnavailable,
  599: ServerError
}


def handle_status(status, data=None):
    """Raise the appropriate error given a status code."""
    if status >= 400:
        error = STATUS_ERRORS.get(status)
        if error is None:
            if status <= 499:
                error = STATUS_ERRORS.get(499)
            elif status <= 599:
                error = STATUS_ERRORS.get(599)
            else:
                error = Error
        errorException = error(data) if data else error()
        raise errorException
