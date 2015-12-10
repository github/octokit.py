# -*- coding: utf-8 -*-

"""
octokit.client
~~~~~~~~~~~~~~

This module contains the main Client class for octokit.py
"""

import requests

from .repository import Repository
from .pagination import Pagination
from .ratelimit import RateLimit
from .exceptions import handle_status, NotFound
from .resources import Resource


class BaseClient(Resource):
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

    def __init__(self, session=requests.Session(),
                 api_endpoint='https://api.github.com', **kwargs):
        self.session = session
        self.url = api_endpoint
        self.schema = {}
        self.name = 'Client'
        self.last_response = None
        self.auto_paginate = False

        self.session.hooks = dict(response=self.response_callback)
        for key in kwargs:
            setattr(self.session, key, kwargs[key])

    def __getattr__(self, name):
        try:
            return super(BaseClient, self).__getattr__(name)
        except AttributeError:
            handle_status(404)

    def response_callback(self, r, *args, **kwargs):
        self.last_response = r
        data = r.json() if r.text != "" else {}
        handle_status(r.status_code, data)

    def bool_from_response(self, method):
        try:
            method()
            return self.last_response.status_code == 204
        except NotFound:
            return False


class Client(Repository, Pagination, RateLimit, BaseClient):
    pass
