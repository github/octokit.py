# -*- coding: utf-8 -*-

"""
octokit.resources
~~~~~~~~~~~~~~~~~

This module contains the workhorse of octokit.py, the Resources.
"""

from .exceptions import handle_status

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
    return get(**kwargs)

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
    if variables:
      raise Exception("You need to call this resource with variables %s" % repr(list(variables)))

    self.schema = self.fetch_schema(self.url)

  def fetch_schema(self, method, url):
    data = self.fetch_resource(method, url)
    data_type = type(data)
    if data_type == dict:
      return self.parse_schema_dict(data)
    elif data_type == list:
      return self.parse_schema_list(data, self.name)
    else:
      raise Exception("Unknown type of response from the API.")

  def fetch_resource(self, method, **kwargs):
    response = method(url, **kwargs)
    handle_status(response.status_code)
    return response.json()

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
  # options - Hash of option to configure the API request.
  #           :headers - Hash of API headers to set.
  #           :query   - Hash of URL query params to set.
  def head(self, options=None):
    options = options or {}
    return elf.call(self.session.head, options)

  # Public: Makes an API request with the curent Relation using GET.
  #
  # options - Hash of option to configure the API request.
  #           :headers - Hash of API headers to set.
  #           :query   - Hash of URL query params to set.
  def get(self, options=None):
    options = options or {}
    return self.call(self.session.get, options)

  # Public: Makes an API request with the curent Relation using POST.
  #
  # data    - The Optional Hash or Resource body to be sent.
  # options - Hash of option to configure the API request.
  #           :headers - Hash of API headers to set.
  #           :query   - Hash of URL query params to set.
  def post(data=None, options=None):
    options = options or {}
    return self.call(self.session.post, data, options)

  # Public: Makes an API request with the curent Relation using PUT.
  #
  # data    - The Optional Hash or Resource body to be sent.
  # options - Hash of option to configure the API request.
  #           :headers - Hash of API headers to set.
  #           :query   - Hash of URL query params to set.
  def put(data=None, options=None):
    options = options or {}
    return self.call(self.session.put, data, options)

  # Public: Makes an API request with the curent Relation using PATCH.
  #
  # data    - The Optional Hash or Resource body to be sent.
  # options - Hash of option to configure the API request.
  #           :headers - Hash of API headers to set.
  #           :query   - Hash of URL query params to set.
  def patch(self, data=None, options=None):
    options = options or {}
    return self.call(self.session.patch, data, options)

  # Public: Makes an API request with the curent Relation using DELETE.
  #
  # data    - The Optional Hash or Resource body to be sent.
  # options - Hash of option to configure the API request.
  #           :headers - Hash of API headers to set.
  #           :query   - Hash of URL query params to set.
  def delete(self, data=None, options=None):
    options = options or {}
    return self.call(self.session.delete, data, options)

  # Public: Makes an API request with the curent Relation using OPTIONS.
  #
  # data    - The Optional Hash or Resource body to be sent.
  # options - Hash of option to configure the API request.
  #           :headers - Hash of API headers to set.
  #           :query   - Hash of URL query params to set.
  def options(self, data=None, opt=None):
    opt = opt or {}
    return self.call(self.session.options, data, opt)

  # Public: Makes an API request with the curent Relation.
  #
  # method  - HTTP method.
  # data    - The Optional Hash or Resource body to be sent.  :get or :head
  #           requests can have no body, so this can be the options Hash
  #           instead.
  # options - Hash of option to configure the API request.
  #           :headers - Hash of API headers to set.
  #           :query   - Hash of URL query params to set.
  #
  def call(self, method, data=None, options=None):
    # If there is only one variable, we don't need kwargs.
    variables = self.variables()
    if len(args) == 1 and len(variables) == 1:
      kwargs[variables.pop()] = args[0]

    url = uritemplate.expand(self.url, kwargs)
    schema = self.fetch_schema(method, url)
    resource = Resource(self.session, schema=schema, url=url, name=humanize(self.name))
    return resource
