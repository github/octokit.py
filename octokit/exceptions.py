# -*- coding: utf-8 -*-

"""
octokit.exceptions
~~~~~~~~~~~~~~~~~~

This module contains octokit.py exceptions.
"""


class Error(Exception):
  """ Something went wrong. """
  def __init__(self):
    self.message = "Something went wrong."
  def __init__(self, data):
    if data is None:
      self.__init__()
    else:
      self.message = data['message']
  def __str__(self):
    return repr(self.message)

class BadRequest(Error):
  """ Status 400: Bad request. """

class Unauthorized(Error):
  """ Status 401/403: Not authorized to view the resource """

class NotFound(Error):
  """ Status 404: The resource wasn't found. """

class MethodNotAllowed(Error):
  """ Status 405: The method is not allowed. """

class NotAcceptable(Error):
  """ Status 406: The response is unacceptable. """

class Conflict(Error):
  """ Status 409: There was a conflict with the current state of the resource. """

class UnsupportedMediaType(Error):
  """ Status 415: Unsupported media type. """

class UnprocessableEntity(Error):
  """ Status 422: Unprocessable entity. """

class ClientError(Error):
  """ Status 4xx: Client error. """

class InternalServerError(Error):
  """ Status 500: Internal server error. """

class NotImplemented(Error):
  """ Status 501: Not implemented. """

class BadGateway(Error):
  """ Status 502: Bad gateway. """

class ServiceUnavailable(Error):
  """ Status 503: Service unavailable. """

class ServerError(Error):
  """ Status 5xx: Server error. """

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

def handle_status(status, data):
  """ Raise the appropriate error given a status code. """
  if status >= 400:
    error = STATUS_ERRORS.get(status)
    if error is None:
      if status <= 499:
        error = STATUS_ERRORS.get(499)
      elif status <= 599:
        error = STATUS_ERRORS.get(599)
      else:
        error = Error
    raise error(data)
