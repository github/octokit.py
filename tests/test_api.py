import unittest

import octokit
from .util import MockOctokitTestCase


class TestApi(MockOctokitTestCase):
    def test_current_user(self):
        login = self.client.current_user.login
        assert login == self.login

    def test_user(self):
        login = self.client.user(self.login).login
        assert login == self.login

if __name__ == '__main__':
    unittest.main()
