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
    variables = self.variables()
    if len(args) == 1 and len(variables) == 1:
      kwargs[variables.pop()] = args[0]

    return self.get(**kwargs)

  def __repr__(self):
    self.ensure_schema_loaded()
    schema_type = type(self.schema)
    if schema_type == dict:
      subtitle = ", ".join(self.schema.keys())
    elif schema_type == list:
      subtitle = str(len(self.schema))

    return "<Octokit %s(%s)>" % (self.name, subtitle)

  def variables(self):
    return uritemplate.variables(self.url)

  def keys(self):
    self.ensure_schema_loaded()
    return self.schema.keys()

  def ensure_schema_loaded(self):
    if self.schema:
      return

    variables = self.variables()
    # if variables:
    #   raise Exception("You need to call this resource with variables %s" % repr(list(variables)))

    url = uritemplate.expand(self.url, {})
    req = requests.Request('GET', url)
    self.schema = self.fetch_schema(req)

    # todo (eduardo) - Rethink the default options
  def fetch_schema(self, req):
    req = self.session.prepare_request(req)
    response = self.session.send(req)
    handle_status(response.status_code)
    data = response.json()
    data_type = type(data)
    if data_type == dict:
      return self.parse_schema_dict(data)
    elif data_type == list:
      return self.parse_schema_list(data, self.name)
    else:
      # todo (eduardo) -- hande request that don't return anything
      raise Exception("Unknown type of response from the API.")

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

  def parse_schema_list(self, data, name):
    schema = []
    for resource in data:
      name = humanize(singularize(name))
      resource = Resource(self.session, schema=resource, name=name)
      schema.append(resource)

    return schema

  # Public: Makes an API request with the resource using HEAD.
  #
  # **kwargs – Optional arguments that request takes
  def head(self, request_params={}, **kwargs):
    return self.fetch_resource('HEAD', request_params, **kwargs)

  # Public: Makes an API request with the curent resource using GET.
  #
  # **kwargs – Optional arguments that request takes
  def get(self, request_params={}, **kwargs):
    return self.fetch_resource('GET', request_params, **kwargs)

  # Public: Makes an API request with the curent resource using POST.
  #
  # **kwargs – Optional arguments that request takes
  def post(request_params={}, **kwargs):
    return self.fetch_resource('POST', request_params, **kwargs)

  # Public: Makes an API request with the curent resource using PUT.
  #
  # **kwargs – Optional arguments that request takes
  def put(self, request_params={}, **kwargs):
    return self.fetch_resource('PUT', request_params, **kwargs)

  # Public: Makes an API request with the curent resource using PATCH.
  #
  # **kwargs – Optional arguments that request takes
  def patch(self, request_params={}, **kwargs):
    return self.fetch_resource('PATCH', request_params, **kwargs)

  # Public: Makes an API request with the curent resource using DELETE.
  #
  # **kwargs – Optional arguments that request takes
  def delete(self, request_params={}, **kwargs):
    return self.fetch_resource('DELETE', request_params, **kwargs)

  # Public: Makes an API request with the curent resource using OPTIONS.
  #
  # **kwargs – Optional arguments that request takes
  def options(self, request_params={}, **kwargs):
    return self.fetch_resource('OPTIONS', request_params, **kwargs)

  # Public: Makes an API request with the curent resource
  #
  # method  - HTTP method.
  # **kwargs – Optional arguments that request takes
  def fetch_resource(self, method, request_params, **kwargs):
    url = uritemplate.expand(self.url, kwargs)
    req = requests.Request(method, url, **request_params)

    schema = self.fetch_schema(req)
    resource = Resource(self.session, schema=schema, url=url, name=humanize(self.name))
    return resource
