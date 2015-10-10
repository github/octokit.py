
from __future__ import print_function
import unittest
import os

import octokit

import requests_mock
import uritemplate

class OctokitTestCase(unittest.TestCase):
  def setUp(self):
    self.username = os.environ['OCTOKIT_TEST_GITHUB_LOGIN']
    self.token = os.environ['OCTOKIT_TEST_GITHUB_TOKEN']
    auth = (self.username, self.token)
    self.client = octokit.Client(auth=auth)

  # def test_authentication(self):
  #   assert self.client.current_user.login == self.username

  # def test_true(self):
  #   assert True

class HttpVerbTestCase(unittest.TestCase):
  def setUp(self):
    self.client = octokit.Client(api_endpoint='mock://api.com/{param}')
    self.adapter = requests_mock.Adapter()
    self.client.session.mount('mock', self.adapter)

  # Basic test to ensure that the HTTP verbs in Resource works as 
  # intended when a valid body is sent.
  def test_http_verbs_basic(self):
    verbs_to_methods = [
      ('GET', self.client.get),
      ('POST', self.client.post),
      ('PUT', self.client.put),
      ('PATCH', self.client.patch),
      ('DELETE', self.client.delete),
      ('HEAD', self.client.head),
      ('OPTIONS', self.client.options),
    ]

    for verb, method in verbs_to_methods:
      url = uritemplate.expand(self.client.url, {'param':'foo'})
      self.adapter.register_uri(verb, url, text='{"success": true}')

      response = method(param='foo')
      assert response.success


if __name__ == '__main__':
  unittest.main()
