import calendar
import time
from collections import namedtuple
try:
  from urllib.parse import urljoin
except ImportError:
  from urlparse import urljoin

class RateLimit(object):
  def __init__(self, *args, **kwargs):
    self._rate_limit = _RateLimit()
    self.last_response = None
    super(RateLimit, self).__init__(*args, **kwargs)

  def response_callback(self, r, **kwargs):
    self.last_response = r
    return super(RateLimit, self).response_callback(r, **kwargs)

  @property
  def rate_limit(self):
    self.update_rate_limit()
    return self._rate_limit

  def update_rate_limit(self):
    if not self.last_response:
      self.head()

    rate_limit = self._rate_limit
    response = self.last_response

    rate_limit.limit = int(response.headers['X-RateLimit-Limit'])
    rate_limit.remaining = int(response.headers['X-RateLimit-Remaining'])
    rate_limit.resets_at = int(response.headers['X-RateLimit-Reset'])
    delta = rate_limit.resets_at - calendar.timegm(time.gmtime())
    rate_limit.resets_in = max(delta, 0)

class _RateLimit(object):
  def __init__(self):
    __slots__ = ('limit', 'remaining', 'resets_at', 'resets_in')

  def __repr__(self):
    return '%s(%s)>' % (self.__class__, self.__dict__)
