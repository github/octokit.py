import base64
import os
import unittest

import betamax
from betamax.fixtures import unittest

import octokit


class MockOctokitTestCase(unittest.BetamaxTestCase):
    """unittest test case that wraps and configures betamax for tests that
    require mocking HTTP requests in octokit.py
    """

    def setUp(self):
        self.login = os.environ.get('OCTOKIT_TEST_GITHUB_LOGIN', 'api-padawan')
        self.token = os.environ.get('OCTOKIT_TEST_GITHUB_TOKEN', 'X'*10)
        with betamax.Betamax.configure() as config:
            config.cassette_library_dir = 'tests/cassettes'

            record_mode = 'never' if os.environ.get('TRAVIS') else 'once'
            config.default_cassette_options['record_mode'] = record_mode

            config.define_cassette_placeholder(
                '<BASIC_AUTH>',
                base64.b64encode(
                    '{}:{}'.format(self.login, self.token).encode()
                ).decode()
            )

        super(MockOctokitTestCase, self).setUp()
        self.client = octokit.Client()
        self.session.auth = (self.login, self.token)
        self.client.session = self.session
