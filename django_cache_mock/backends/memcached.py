import logging
from functools import cached_property

from django.core.cache.backends.memcached import BaseMemcachedCache, PyMemcacheCache

logger = logging.getLogger(__name__)


class MockcacheCache(BaseMemcachedCache):
    _dbs = {}

    def __init__(self, server, params):
        import mockcache

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


class PyMemcacheMockMemcacheCache(PyMemcacheCache):
    _dbs = {}

    def __init__(self, server, params):
        from pymemcache.test.utils import MockMemcacheClient

        super().__init__(server, params)
        self._class = MockMemcacheClient
        self.location = server

    @cached_property
    def _cache(self):
        client = super()._cache
        client._contents = self._dbs.setdefault(self.location, {})
        return client
