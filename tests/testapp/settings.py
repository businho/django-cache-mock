import django_cache_mock.mock

USE_TZ = True

CACHES = {
    cache_alias: {"BACKEND": cache_class}
    for cache_alias, cache_class in django_cache_mock.mock.SUPPORTED_BACKENDS.items()
}
