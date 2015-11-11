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
    super(RateLimit, self).__init__(*args, **kwargs)

  @property
  def rate_limit(self):
    self.update_rate_limit()
    return self._rate_limit

  def fetch_rate_limit(self):
    # TODO (eduardo) : Find a better way to join url with api_endpoint so we
    # don't need to do it for every REST call
    endpoint = urljoin(self.agent.endpoint, 'rate_limit')
    self.last_response = self.get(endpoint).response

  def update_rate_limit(self):
    if not self.last_response:
      self.fetch_rate_limit()

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
