import logging
from functools import cached_property

from django.utils.functional import SimpleLazyObject

logger = logging.getLogger(__name__)

try:
    from django.core.cache.backends.redis import RedisCache, RedisCacheClient

    logger.debug("Using Django built-in redis cache.")

    class _RedisCacheClient(RedisCacheClient):
        def get_client(self, key=None, *, write=False):
            return self._client(**self._options)

    class BaseRedisCache(RedisCache):
        def __init__(self, server, params):
            if not server:
                server = self.library.__name__

            super().__init__(server, params)
            self._lib = self.library
            self._client = self.client_class
            self._class = _RedisCacheClient

        @cached_property
        def _cache(self):
            client = super()._cache
            client._lib = self._lib
            client._client = self._client
            client._options = dict(**self.redis_client_cls_kwargs, **self._options)
            return client

except ImportError:
    # Django<4 don´t have built-in RedisCache.
    from django_redis.cache import RedisCache
    from django_redis.pool import ConnectionFactory

    logger.debug("Using django-redis.")

    class _ConnectionFactory(ConnectionFactory):
        def get_connection(self, params):
            return self.redis_client_cls(**self.redis_client_cls_kwargs)

    class BaseRedisCache(RedisCache):
        def __init__(self, server, params):
            if not server:
                server = self.library.__name__

            super().__init__(server, params)

        @property
        def client(self):
            if self._client is None:
                self._client = super().client
                redis_client_class = (
                    f"{self.client_class.__module__}.{self.client_class.__name__}"
                )
                self._client.connection_factory = _ConnectionFactory(
                    options={
                        "REDIS_CLIENT_CLASS": redis_client_class,
                        "REDIS_CLIENT_KWARGS": self.redis_client_cls_kwargs,
                    },
                )
            return self._client


try:
    import redislite

    class RedisLiteCache(BaseRedisCache):
        library = redislite
        client_class = redislite.StrictRedis

        def __init__(self, server, params):
            self.dbfilename = server or "redislite.db"
            super().__init__(server, params)

        @property
        def redis_client_cls_kwargs(self):
            return {"dbfilename": self.dbfilename}

except ImportError as exc:
    logger.debug("redislite is not installed.")

    _import_error = exc

    class RedisLiteCache:
        def __init__(self, server, params):
            raise _import_error


try:
    import fakeredis

    class FakeRedisCache(BaseRedisCache):
        _fake_server = SimpleLazyObject(lambda: fakeredis.FakeServer())
        client_class = fakeredis.FakeStrictRedis
        library = fakeredis

        @property
        def redis_client_cls_kwargs(self):
            return {"server": self._fake_server}

except ImportError as exc:
    logger.debug("fakeredis is not installed.")

    _import_error = exc

    class FakeRedisCache:
        def __init__(self, server, params):
            raise _import_error
