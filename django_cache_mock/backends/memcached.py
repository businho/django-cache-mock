import logging
from functools import cached_property

from django.core.cache.backends.memcached import BaseMemcachedCache, PyMemcacheCache

from django_cache_mock.exceptions import LazyLibImportError

logger = logging.getLogger(__name__)


try:
    import mockcache

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

except ImportError as _import_error:
    logger.debug("mockcache is not installed.")

    class MockcacheCache(LazyLibImportError):
        parent_exception = _import_error


try:
    from pymemcache.test.utils import MockMemcacheClient

    class PyMemcacheMockMemcacheCache(PyMemcacheCache):
        _dbs = {}

        def __init__(self, server, params):
            super().__init__(server, params)
            self._class = MockMemcacheClient
            self.location = server

        @cached_property
        def _cache(self):
            client = super()._cache
            client._contents = self._dbs.setdefault(self.location, {})
            return client

except ImportError as _import_error:
    logger.debug("pymemcache is not installed.")

    class PyMemcacheMockMemcacheCache(LazyLibImportError):
        parent_exception = _import_error
