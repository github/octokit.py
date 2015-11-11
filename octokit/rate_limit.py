class RateLimit(object):
  def __init__(self):
    __slots__ = ('limit', 'remaining', 'resets_at', 'resets_in')
