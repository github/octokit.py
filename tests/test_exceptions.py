import unittest

import requests_mock

import octokit


class TestExceptions(unittest.TestCase):
    """Tests the exception handling code in octokit/exceptions.py"""

    def setUp(self):
        self.client = octokit.Client(api_endpoint='mock://api.com/')
        self.adapter = requests_mock.Adapter()
        self.client.session.mount('mock', self.adapter)

    def test_exceptions(self):
        """Test that HTTP response status codes raise the correct errors."""
        for status_code, exception in octokit.exceptions.STATUS_ERRORS.items():
            self.adapter.register_uri(
                'GET',
                self.client.url,
                status_code=status_code
            )

            with self.assertRaises(exception):
                self.client.get()

if __name__ == '__main__':
    unittest.main()
