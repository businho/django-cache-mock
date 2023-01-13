from functools import cached_property

import mockcache
from django.core.cache.backends.memcached import BaseMemcachedCache


class MockcacheCache(BaseMemcachedCache):
    _dbs = {}

    def __init__(self, server, params):
        super().__init__(
            server,
            params,
            library=mockcache,
            value_not_found_exception=ValueError,
        )
        self.location = server

    def get(self, key, default=None, version=None):
        # Override method because library don't support a default value.
        key = self.make_key(key, version=version)
        self.validate_key(key)
        val = self._cache.get(key)
        if val is None:
            return default
        return val

    @cached_property
    def _cache(self):
        client = super()._cache
        client.dictionary = self._dbs.setdefault(self.location, {})
        return client
