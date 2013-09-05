# -*- coding: utf-8 -*-

"""
octokit.resources
~~~~~~~~~~~~~~~~~

This module contains the workhorse of octokit.py, the Resources.
"""

from .exceptions import handle_status

class Resource(object):
  """The workhorse of octokit.py, this class makes the API calls and interprets
  them into an accessible schema. The API calls and schema parsing are lazy and
  only happen when an attribute of the resource is requested.
  """

  def __init__(self, root_url, session):
    self.session = session
    self.root_url = root_url
    self.schema = {}

  def __getattr__(self, name):
    self.ensure_schema_loaded()
    if name in self.schema:
      return self.schema[name]
    else:
      raise handle_status(404)

  def keys(self):
    self.ensure_schema_loaded()
    return self.schema.keys()

  def ensure_schema_loaded(self):
    if not self.schema:
      self.load_schema()

  def load_schema(self):
    data = self.fetch_resource(self.root_url)
    self.schema = self.parse_schema(data)

  def fetch_resource(self, url):
    response = self.session.get(url)
    handle_status(response.status_code)
    return response.json()

  def parse_schema(self, data):
    schema = {}
    for key in data:
      name = key.split('_url')[0]
      if key.endswith('_url'):
        schema[name] = Resource(data[key], self.session)
      else:
        schema[name] = data[key]
    return schema
