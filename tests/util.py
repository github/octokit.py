import base64
import os
import unittest

import betamax

import octokit

class MockOctokitTestCase(unittest.TestCase):
    """unittest test case that wraps and configures betamax for tests that
    require mocking HTTP requests in octokit.py
    """

    def setUp(self):
        self.login = os.environ.get('OCTOKIT_TEST_GITHUB_LOGIN', 'api-padawan')
        self.token = os.environ.get('OCTOKIT_TEST_GITHUB_TOKEN', 'X'*10)
        self.client = octokit.Client(auth=(self.login, self.token))
        self.session = self.client.session
        self.recorder = betamax.Betamax(self.session)

        with betamax.Betamax.configure() as config:
            config.cassette_library_dir = 'tests/cassettes'

            record_mode = 'never' if os.environ.get('TRAVIS') else 'once'
            config.default_cassette_options['record_mode'] = record_mode

            config.define_cassette_placeholder(
                '<BASIC_AUTH>',
                base64.b64encode('{}:{}'.format(
                    self.login,
                    self.token
                ).encode()).decode()
            )
