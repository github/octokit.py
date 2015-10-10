# -*- coding: utf-8 -*-

"""
octokit.exceptions
~~~~~~~~~~~~~~~~~~

This module contains octokit.py exceptions.
"""


class Error(Exception):
  """ Something went wrong. """

class NotFound(Error):
  """ Status 404: The resource wasn't found. """

class Unauthorized(Error):
  """ Status 401/403: Not authorized to view the resource """

# Mapping of status code to Exception
STATUS_ERRORS = {
  404: NotFound,
  401: Unauthorized,
  403: Unauthorized
}

def handle_status(status):
  """ Raise the appropriate error given a status code. """
  if status >= 400:
    raise STATUS_ERRORS.get(status, Error)