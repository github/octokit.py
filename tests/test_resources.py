import os
import unittest

import requests_mock
import uritemplate

import octokit

class TestResources(unittest.TestCase):
    """Tests the functionality in octokit/resources.py"""

    def setUp(self):
        self.client = octokit.Client(api_endpoint='mock://api.com/{param}')
        self.adapter = requests_mock.Adapter()
        self.client.session.mount('mock', self.adapter)

    def test_call(self):
        """Test that resources.__call__ performs a HTTP GET"""
        url = uritemplate.expand(self.client.url, {'param': 'foo'})
        self.adapter.register_uri('GET', url, text='{"success": true}')

        response = self.client(param='foo')
        assert response.success

        # test named param inference
        response = self.client('foo')
        assert response.success

    def test_httpverb(self):
        """Test that each HTTP verb functions properly when JSON is returned."""
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
            url = uritemplate.expand(self.client.url, {'param': 'foo'})
            self.adapter.register_uri(verb, url, text='{"success": true}')

            response = method(param='foo')
            assert response.success

            # test named param inference
            response = method('foo')
            assert response.success

    def test_pagination(self):
      self.client.auto_paginate = True
      url = uritemplate.expand(self.client.url, {'param':'foo'})

      headers1 = {
        'Link': '<'+url+'?page=2&per_page=100>; rel="next"',
        'X-RateLimit-Remaining': '56',
        'X-RateLimit-Reset': '1446804464',
        'X-RateLimit-Limit': '60'
      }
      headers2 = {
        'Link': '<'+url+'?page=3&per_page=100>; rel="next"',
        'X-RateLimit-Remaining': '56',
        'X-RateLimit-Reset': '1446804464',
        'X-RateLimit-Limit': '60'
      }
      headers3 = {
        'X-RateLimit-Remaining': '56',
        'X-RateLimit-Reset': '1446804464',
        'X-RateLimit-Limit': '60'
      }
      data1 = '["a","b"]'
      data2 = '["c","d"]'
      data3 = '["e","f"]'

      self.adapter.register_uri('GET', url, headers=headers1, text=data1)
      self.adapter.register_uri('GET', url+'?page=2', headers=headers2, text=data2)
      self.adapter.register_uri('GET', url+'?page=3', headers=headers3, text=data3)

      response = self.client.paginate(self.client.url, param='foo')
      resultSchema = [r.schema for r in response.schema]
      expectedSchema = ['a', 'b', 'c', 'd', 'e', 'f']

      self.assertEqual(resultSchema, expectedSchema)

    def test_rate_limit(self):
      self.client.auto_paginate = True
      url = uritemplate.expand(self.client.url, {'param':'foo'})

      headers1 = {
        'Link': '<'+url+'?page=2>; rel="next"',
        'X-RateLimit-Remaining': '1',
        'X-RateLimit-Reset': '1446804464',
        'X-RateLimit-Limit': '60'
      }
      headers2 = {
        'Link': '<'+url+'?page=3>; rel="next"',
        'X-RateLimit-Remaining': '0',
        'X-RateLimit-Reset': '1446804464',
        'X-RateLimit-Limit': '60'
      }
      headers3 = {
        'X-RateLimit-Remaining': '0',
        'X-RateLimit-Reset': '1446804464',
        'X-RateLimit-Limit': '60'
      }
      data1 = '["a","b"]'
      data2 = '["c","d"]'
      data3 = '["e","f"]'

      self.adapter.register_uri('GET', url, headers=headers1, text=data1)
      self.adapter.register_uri('GET', url+'?page=2', headers=headers2, text=data2)
      self.adapter.register_uri('GET', url+'?page=3', headers=headers3, text=data3)

      response = self.client.paginate(url=self.client.url, param='foo')
      resultSchema = [r.schema for r in response.schema]
      expectedSchema = ['a', 'b', 'c', 'd']

      self.assertEqual(resultSchema, expectedSchema)

if __name__ == '__main__':
    unittest.main()
