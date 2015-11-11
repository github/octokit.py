# -*- coding: utf-8 -*-

"""
octokit.client
~~~~~~~~~~~~~~

This module contains the main Client class for octokit.py
"""

# https://code.google.com/p/uri-templates/wiki/Implementations

from .resources import Resource
from .session import Session


class Client(Resource):
  """The main class for using octokit.py.

  This class accepts as arguments any attributes that can be set on a
  Requests.Session() object. After instantiation, the session may be modified
  by accessing the `session` attribute.

  Example usage:

    >>> client = octokit.Client(auth = ('mastahyeti', 'oauth-token'))
    >>> client.session.proxies = {'http': 'foo.bar:3128'}
    >>> client.current_user.login
    'mastahyeti'
  """

  def __init__(self, api_endpoint='https://api.github.com', **kwargs):
    self.session = Session(**kwargs)
    self.url = api_endpoint
    self.schema = {}
    self.name = 'Client'
