USE_TZ = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    "mockcache": {
        "BACKEND": "django_cache_mock.backends.memcached.MockcacheCache",
    },
    "fakeredis": {
        "BACKEND": "django_cache_mock.backends.redis.FakeRedisCache",
    },
    "redislite": {
        "BACKEND": "django_cache_mock.backends.redis.RedisLiteCache",
    },
}
