from .rate_limit import RateLimit

import calendar
import requests
import time


class Session(object):
  def __init__(self, **kwargs):
    self.session = requests.Session()
    self.rate_limit = RateLimit()
    self.last_response = None

    self.auto_paginate = None
    self.per_page = None

    for key in kwargs:
      setattr(self.session, key, kwargs[key])

  def __getattribute__(self, name):
    attr = object.__getattribute__(self, name)
    if name == 'rate_limit':
      self.update_rate_limit(attr)

    return attr

  def __getattr__(self, name):
    return getattr(self.session, name)

  def fetch_rate_limit(self):
    self.last_response = self.session.get('https://api.github.com/rate_limit')

  def update_rate_limit(self, rate_limit):
    if not self.last_response:
      self.fetch_rate_limit()

    response = self.last_response
    rate_limit.limit = int(response.headers['X-RateLimit-Limit'])
    rate_limit.remaining = int(response.headers['X-RateLimit-Remaining'])
    rate_limit.resets_at = int(response.headers['X-RateLimit-Reset'])
    rate_limit.resets_in = max(rate_limit.resets_at - calendar.timegm(time.gmtime()), 0)
