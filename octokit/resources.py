# -*- coding: utf-8 -*-

"""
octokit.resources
~~~~~~~~~~~~~~~~~

This module contains the workhorse of octokit.py, the Resources.
"""

from .exceptions import handle_status

import requests
import uritemplate
from inflection import humanize, singularize

class Resource(object):
  """The workhorse of octokit.py, this class makes the API calls and interprets
  them into an accessible schema. The API calls and schema parsing are lazy and
  only happen when an attribute of the resource is requested.
  """

  def __init__(self, session, url=None, schema=None, name=None):
    self.session = session
    self.url = url
    self.name = name
    self.rels = {}

    if type(schema) == dict and 'url' in schema:
      self.url = schema['url']

    self.schema = schema

  def __getattr__(self, name):
    self.ensure_schema_loaded()
    if name in self.schema:
      return self.schema[name]
    else:
      raise handle_status(404)

  def __getitem__(self, name):
    self.ensure_schema_loaded()
    return self.schema[name]

  def __call__(self, *args, **kwargs):
    return self.get(*args, **kwargs)

  def __repr__(self):
    self.ensure_schema_loaded()
    schema_type = type(self.schema)
    if schema_type == dict:
      subtitle = ', '.join(self.schema.keys())
    elif schema_type == list:
      subtitle = str(len(self.schema))
    else:
      subtitle = str(self.schema)

    return '<Octokit %s(%s)>' % (self.name, subtitle)

  # Returns the variables the URI takes
  def variables(self):
    return uritemplate.variables(self.url)

  # Returns the links this resource can follow
  def keys(self):
    self.ensure_schema_loaded()
    return self.schema.keys()

  # Check if the current resources' schema has been loaded, otherwise load it
  def ensure_schema_loaded(self):
    if self.schema:
      return

    self.schema = self.get().schema

  # Fetch the current request and return its schema
  def parse_schema(self, response):
    # If content of response is empty, then default to empty dictionary
    data = response.json() if response.text != "" else {}
    handle_status(response.status_code, data)
    data_type = type(data)

    if data_type == dict:
      schema = self.parse_schema_dict(data)
    elif data_type == list:
      schema = self.parse_schema_list(data, self.name)
    else:
      # TODO (eduardo) -- handle request that don't return anything
      raise Exception("Unknown type of response from the API.")

    return schema

  # Convert the JSON returned by the request into a dictionary of resources
  def parse_schema_dict(self, data):
    schema = {}
    for key in data:
      name = key.split('_url')[0]
      if key.endswith('_url'):
        if data[key]:
          schema[name] = Resource(self.session, url=data[key], name=humanize(name))
        else:
          schema[name] = data[key]
      else:
        data_type = type(data[key])
        if data_type == dict:
          schema[name] = Resource(self.session, schema=data[key], name=humanize(name))
        elif data_type == list:
          schema[name] = self.parse_schema_list(data[key], name=name)
        else:
          schema[name] = data[key]

    return schema

  # Convert the JSON returned by the request into a dictionary resources
  def parse_schema_list(self, data, name):
    schema = []
    for resource in data:
      name = humanize(singularize(name))
      resource = Resource(self.session, schema=resource, name=name)
      schema.append(resource)

    return schema

  # Parse pagination links from the headers
  def parse_rels(self, response):
    rels = {}
    for link in response.links.values():
      rels[link['rel']] = Resource(self.session, url=link['url'], name=humanize(self.name))

    return rels

  # Continue following the relations until there are no more links
  #
  # *args           - Uri template argument
  # **kwargs        – Uri template arguments
  # Returns Resource
  def paginate(self, *args, **kwargs):
    session = self.session
    if (session.auto_paginate or session.per_page) and 'per_page' not in kwargs:
      # if per page is not defined, default to 100 per page
      kwargs['per_page'] = session.per_page or 100

    resource = self
    data = list(resource.get(*args, **kwargs).schema)

    if session.auto_paginate:
      while 'next' in resource.rels and session.rate_limit.remaining > 0:
        resource = resource.rels['next']
        data.extend(resource.get().schema)

    return Resource(session, schema=data, url=self.url, name=self.name)

  # Makes an API request with the resource using HEAD.
  #
  # *args           - Uri template argument
  # **kwargs        – Uri template arguments
  def head(self, *args, **kwargs):
    return self.fetch_resource('HEAD', *args, **kwargs)

  # Makes an API request with the curent resource using GET.
  #
  # *args           - Uri template argument
  # **kwargs        – Uri template arguments
  def get(self, *args, **kwargs):
    return self.fetch_resource('GET', *args, **kwargs)

  # Makes an API request with the curent resource using POST.
  #
  # *args           - Uri template argument
  # **kwargs        – Uri template arguments
  def post(self, *args, **kwargs):
    return self.fetch_resource('POST', *args, **kwargs)

  # Makes an API request with the curent resource using PUT.
  #
  # *args           - Uri template argument
  # **kwargs        – Uri template arguments
  def put(self, *args, **kwargs):
    return self.fetch_resource('PUT', *args, **kwargs)

  # Makes an API request with the curent resource using PATCH.
  #
  # *args           - Uri template argument
  # **kwargs        – Uri template arguments
  def patch(self, *args, **kwargs):
    return self.fetch_resource('PATCH', *args, **kwargs)

  # Makes an API request with the curent resource using DELETE.
  #
  # *args           - Uri template argument
  # **kwargs        – Uri template arguments
  def delete(self, *args, **kwargs):
    return self.fetch_resource('DELETE', *args, **kwargs)

  # Makes an API request with the curent resource using OPTIONS.
  #
  # *args           - Uri template argument
  # **kwargs        – Uri template arguments
  def options(self, *args, **kwargs):
    return self.fetch_resource('OPTIONS', *args, **kwargs)

  # Public: Makes an API request with the curent resource
  #
  # method         - HTTP method.
  # *args          - Uri template argument
  # **kwargs       – Uri template arguments
  def fetch_resource(self, method, *args, **kwargs):
    variables = self.variables()
    if len(args) == 1 and len(variables) == 1:
      kwargs[next(iter(variables))] = args[0]

    url_args = {k: kwargs[k] for k in kwargs if k in variables}
    req_args = {k: kwargs[k] for k in kwargs if k not in variables}

    url = uritemplate.expand(self.url, url_args)
    request = requests.Request(method, url, **req_args)
    prepared_req = self.session.prepare_request(request)
    response = self.session.send(prepared_req)

    schema = self.parse_schema(response)
    self.rels = self.parse_rels(response)
    self.session.last_response = response

    return Resource(self.session, schema=schema, name=humanize(self.name))
