# -*- coding: utf-8 -*-

"""
octokit.resources
~~~~~~~~~~~~~~~~~

This module contains the workhorse of octokit.py, the Resources.
"""

from inflection import humanize, singularize
import requests
import uritemplate


class Resource(object):
    """The workhorse of octokit.py, this class makes the API calls and
    interprets them into an accessible schema. The API calls and schema parsing
    are lazy and only happen when an attribute of the resource is requested.
    """

    def __init__(self, session, name=None, url=None, schema=None,
                 response=None):
        self.session = session
        self.name = name
        self.url = url
        self.schema = schema
        self.response = response
        self.rels = {}

        if response:
            self.schema = self.parse_schema(response.json())
            self.rels = self.parse_rels(response)
            self.url = response.url

        if type(self.schema) == dict and 'url' in self.schema:
            self.url = self.schema['url']

    def __getattr__(self, name):
        self.ensure_schema_loaded()
        if name in self.schema:
            return self.schema[name]
        else:
            raise AttributeError

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

    def variables(self):
        """Returns the variables the URI takes"""
        return uritemplate.variables(self.url)

    def keys(self):
        """Returns the links this resource can follow"""
        self.ensure_schema_loaded()
        return self.schema.keys()

    def ensure_schema_loaded(self):
        """Check if resources' schema has been loaded, otherwise load it"""
        if self.schema:
            return
        elif self.variables():
            raise Exception("You need to call this resource with variables %s"
                            % repr(list(variables)))

        self.schema = self.get().schema

    def parse_schema(self, response):
        """Parse the response and return its schema"""
        data_type = type(response)

        if data_type == dict:
            schema = self.parse_schema_dict(response)
        elif data_type == list:
            schema = self.parse_schema_list(response, self.name)
        else:
            # TODO (eduardo) -- handle request that don't return anything
            raise Exception("Unknown type of response from the API.")

        return schema

    def parse_schema_dict(self, data):
        """Convert the responses' JSON into a dictionary of resources"""
        schema = {}
        for key in data:
            name = key.split('_url')[0]
            if key.endswith('_url'):
                if data[key]:
                    schema[name] = Resource(self.session, url=data[key],
                                            name=humanize(name))
                else:
                    schema[name] = data[key]
            else:
                data_type = type(data[key])
                if data_type == dict:
                    schema[name] = Resource(self.session, schema=data[key],
                                            name=humanize(name))
                elif data_type == list:
                    schema[name] = self.parse_schema_list(data[key], name=name)
                else:
                    schema[name] = data[key]

        return schema

    def parse_schema_list(self, data, name):
        """Convert the responses' JSON into a list of resources"""
        return [
          Resource(self.session, schema=s, name=humanize(singularize(name)))
          for s in data
        ]

    def parse_rels(self, response):
        """Parse relation links from the headers"""
        return {
          link['rel']: Resource(self.session, url=link['url'], name=self.name)
          for link in response.links.values()
        }

    def head(self, *args, **kwargs):
        """Make a HTTP HEAD request to the endpoint of resource."""
        return self.fetch_resource('HEAD', *args, **kwargs)

    def get(self, *args, **kwargs):
        """Make a HTTP GET request to the endpoint of resource."""
        return self.fetch_resource('GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        """Make a HTTP POST request to the endpoint of resource."""
        return self.fetch_resource('POST', *args, **kwargs)

    def put(self, *args, **kwargs):
        """Make a HTTP PUT request to the endpoint of resource."""
        return self.fetch_resource('PUT', *args, **kwargs)

    def patch(self, *args, **kwargs):
        """Make a HTTP PATCH request to the endpoint of resource."""
        return self.fetch_resource('PATCH', *args, **kwargs)

    def delete(self, *args, **kwargs):
        """Make a HTTP DELETE request to the endpoint of resource."""
        return self.fetch_resource('DELETE', *args, **kwargs)

    def options(self, *args, **kwargs):
        """Make a HTTP OPTIONS request to the endpoint of resource."""
        return self.fetch_resource('OPTIONS', *args, **kwargs)

    def fetch_resource(self, method, *args, **kwargs):
        """Fetch the endpoint from the API and return it as a Resource.

        method         - HTTP method.
        *args          - Uri template argument
        **kwargs       – Uri template arguments
        """
        variables = self.variables()
        if len(args) == 1 and len(variables) == 1:
            kwargs[next(iter(variables))] = args[0]

        url_args = {k: kwargs[k] for k in kwargs if k in variables}
        req_args = {k: kwargs[k] for k in kwargs if k not in variables}

        url = uritemplate.expand(self.url, url_args)
        request = requests.Request(method, url, **req_args)
        prepared_req = self.session.prepare_request(request)
        response = self.session.send(prepared_req)

        return Resource(self.session, response=response,
                        name=humanize(self.name))
