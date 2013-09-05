
from __future__ import print_function
import unittest
import os

import octokit

class OctokitTestCase(unittest.TestCase):
  def setUp(self):
    self.username = os.environ['OCTOKIT_TEST_USER']
    self.token = os.environ['OCTOKIT_TEST_TOKEN']
    auth = (self.username, self.token)
    self.client = octokit.Client(auth=auth)

  def test_authentication(self):
    assert self.client.current_user.login == self.username

if __name__ == '__main__':
    unittest.main()