from .rate_limit import RateLimit

import calendar
import requests
import time

class Session(requests.Session):
  def __init__(self, **kwargs):
    super(Session, self).__init__()
    self._rate_limit = RateLimit()
    self.last_response = None
    self.auto_paginate = None

    for key in kwargs:
      setattr(self, key, kwargs[key])

  @property
  def rate_limit(self):
    self.update_rate_limit()
    return self._rate_limit

  def fetch_rate_limit(self):
    # TODO (eduardo) : generalize api-enpoint
    self.last_response = self.session.get('https://api.github.com/rate_limit')

  def update_rate_limit(self):
    if not self.last_response:
      self.fetch_rate_limit()

    rate_limit = self._rate_limit
    response = self.last_response
    rate_limit.limit = int(response.headers['X-RateLimit-Limit'])
    rate_limit.remaining = int(response.headers['X-RateLimit-Remaining'])
    rate_limit.resets_at = int(response.headers['X-RateLimit-Reset'])
    rate_limit.resets_in = max(rate_limit.resets_at - calendar.timegm(time.gmtime()), 0)
