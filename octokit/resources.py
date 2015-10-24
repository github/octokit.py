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
    self.name = name
    if url:
      self.url = url
      self.schema = {}

    if schema:
      if 'url' in schema:
        self.url = schema['url']
      self.schema = self.parse_schema_dict(schema)

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
      subtitle = ", ".join(self.schema.keys())
    elif schema_type == list:
      subtitle = str(len(self.schema))

    return "<Octokit %s(%s)>" % (self.name, subtitle)

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
  def fetch_schema(self, req):
    req = self.session.prepare_request(req)
    response = self.session.send(req)
    handle_status(response.status_code)
    # If content of response is empty, then default to empty dictionary
    data = response.json() if response.text != "" else {}
    data_type = type(data)
    if data_type == dict:
      return self.parse_schema_dict(data)
    elif data_type == list:
      return self.parse_schema_list(data, self.name)
    else:
      # todo (eduardo) -- hande request that don't return anything
      raise Exception("Unknown type of response from the API.")

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
    req = requests.Request(method, url, **req_args)

    schema = self.fetch_schema(req)
    resource = Resource(self.session, schema=schema, url=url, name=humanize(self.name))
    return resource
