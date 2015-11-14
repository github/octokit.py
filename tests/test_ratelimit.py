import os
import unittest

import requests_mock
import uritemplate

import octokit


class TestRateLimit(unittest.TestCase):
    """Tests the functionality in octokit/ratelimit.py"""

    def setUp(self):
        self.client = octokit.Client(api_endpoint='mock://api.com/{param}')
        self.adapter = requests_mock.Adapter()
        self.client.session.mount('mock', self.adapter)

    def test_rate_limit(self):
        self.client.auto_paginate = True
        url = uritemplate.expand(self.client.url, {'param': 'foo'})

        h1 = {
            'Link': '<'+url+'?page=2>; rel="next"',
            'X-RateLimit-Remaining': '1',
            'X-RateLimit-Reset': '1446804464',
            'X-RateLimit-Limit': '60'
        }
        h2 = {
            'Link': '<'+url+'?page=3>; rel="next"',
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': '1446804464',
            'X-RateLimit-Limit': '60'
        }
        h3 = {
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': '1446804464',
            'X-RateLimit-Limit': '60'
        }
        res1 = '["a","b"]'
        res2 = '["c","d"]'
        res3 = '["e","f"]'

        self.adapter.register_uri('GET', url, headers=h1, text=res1)
        self.adapter.register_uri('GET', url+'?page=2', headers=h2, text=res2)
        self.adapter.register_uri('GET', url+'?page=3', headers=h3, text=res3)

        response = self.client.paginate(param='foo')
        resultSchema = [r.schema for r in response.schema]
        expectedSchema = ['a', 'b', 'c', 'd']

        self.assertEqual(resultSchema, expectedSchema)

if __name__ == '__main__':
    unittest.main()
