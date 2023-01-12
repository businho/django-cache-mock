import logging

SUPPORTED_BACKENDS = {
    "mockcache": "django_cache_mock.backends.memcached.MockcacheCache",
    "fakeredis": "django_cache_mock.backends.redis.FakeRedisCache",
    "redislite": "django_cache_mock.backends.redis.RedisLiteCache",
}

logger = logging.getLogger(__name__)


def patch(caches, cache_alias, backend, params=None, *, force=False):
    current_config = caches[cache_alias]
    location = current_config.get("LOCATION")
    if location and not force:
        logger.debug(f"Skipped cache {cache_alias} patch because LOCATION is defined.")
        return False

    if params is None:
        params = {}

    params["BACKEND"] = SUPPORTED_BACKENDS[backend]
    logger.info(f"Cache {cache_alias} mocked with {backend}.")
    logger.debug(f"{params=}.")
    caches[cache_alias] = params
    return True
