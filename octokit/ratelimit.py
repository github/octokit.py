import calendar
import time


class RateLimit(object):
    def __init__(self, *args, **kwargs):
        self._rate_limit = _RateLimit()
        print(type(super(RateLimit, self)))
        super(RateLimit, self).__init__(*args, **kwargs)

    @property
    def rate_limit(self):
        self.update_rate_limit()
        return self._rate_limit

    def update_rate_limit(self):
        if not self.last_response:
            self.head()

        rate_limit = self._rate_limit
        headers = self.last_response.headers

        rate_limit.limit = int(headers['X-RateLimit-Limit'])
        rate_limit.remaining = int(headers['X-RateLimit-Remaining'])
        rate_limit.resets_at = int(headers['X-RateLimit-Reset'])
        delta = rate_limit.resets_at - calendar.timegm(time.gmtime())
        rate_limit.resets_in = max(delta, 0)


class _RateLimit(object):
    __slots__ = ('limit', 'remaining', 'resets_at', 'resets_in')

    def __repr__(self):
        s = ', '.join(
            '{}={}'.format(slot, getattr(self, slot))
            for slot in self.__slots__
        )
        return '%s(%s)' % (self.__class__, s)
