import logging

SUPPORTED_BACKENDS = {
    "mockcache": "django_cache_mock.backends.memcached.MockcacheCache",
    "fakeredis": "django_cache_mock.backends.redis.FakeRedisCache",
    "redislite": "django_cache_mock.backends.redis.RedisLiteCache",
    "fakeredis[django-redis]": (
        "django_cache_mock.backends.redis.FakeRedisDjangoRedisCache"
    ),
    "redislite[django-redis]": (
        "django_cache_mock.backends.redis.RedisLiteDjangoRedisCache"
    ),
}

logger = logging.getLogger(__name__)


def patch(caches, cache_alias, backend, params=None, *, force=False):
    current_config = caches[cache_alias]
    current_location = current_config.get("LOCATION")

    if params is None:
        params = {}

    if current_location and not force:
        logger.debug(f"Skipped cache {cache_alias} patch because LOCATION is defined.")
        return False

    current_backend = current_config.get("BACKEND", "")
    backend = _redis_backend(current_backend, cache_alias, backend)

    params["BACKEND"] = SUPPORTED_BACKENDS[backend]
    logger.info(f"Cache {cache_alias} mocked with {backend}.")
    logger.debug(f"{params=}.")
    caches[cache_alias] = params
    return True


def _redis_backend(current_backend, cache_alias, backend):
    if "redis" not in backend or "django-redis" in backend:
        return backend

    if "django_redis" in current_backend:
        backend += "[django-redis]"

    return backend
