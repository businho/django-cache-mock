from unittest.mock import sentinel

import pytest

from django_cache_mock import patch
from django_cache_mock.mock import SUPPORTED_BACKENDS


def test_do_not_patch_when_location_is_defined():
    caches = {"default": {"LOCATION": sentinel.location}}
    patch(caches, "default", "mockcache")
    assert caches["default"]["LOCATION"] == sentinel.location


def test_patch_forced_when_location_is_defined():
    caches = {"default": {"LOCATION": sentinel.location}}
    patch(caches, "default", "mockcache", force=True)
    expected_backend = "django_cache_mock.backends.memcached.MockcacheCache"
    assert caches["default"]["BACKEND"] == expected_backend


def test_fail_for_cache_unknown():
    with pytest.raises(KeyError):
        patch({}, "default", "mockcache")


def test_fail_for_backend_unknown():
    with pytest.raises(KeyError):
        patch({"default": {}}, "default", "fakefake")


def test_custom_params():
    caches = {"default": {"FOO": sentinel.foo}}
    patch(caches, "default", "mockcache", {"BAR": sentinel.bar})
    assert "FOO" not in caches["default"]
    assert caches["default"]["BAR"] == sentinel.bar


def test_use_django_builtin_redis_based_on_backend(redis_backend):
    caches = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache"}}
    patch(caches, "default", redis_backend)
    expected_backend = SUPPORTED_BACKENDS[redis_backend]
    assert caches["default"] == {
        "BACKEND": expected_backend,
    }


def test_use_django_redis_based_on_backend(redis_backend):
    caches = {"default": {"BACKEND": "django_redis.cache.RedisCache"}}
    patch(caches, "default", redis_backend)
    expected_backend = SUPPORTED_BACKENDS[f"{redis_backend}[django-redis]"]
    assert caches["default"] == {
        "BACKEND": expected_backend,
    }


def test_use_django_redis_explicit(redis_backend):
    caches = {"default": {}}
    explicit_django_redis_backend = f"{redis_backend}[django-redis]"
    patch(caches, "default", explicit_django_redis_backend)
    expected_backend = SUPPORTED_BACKENDS[explicit_django_redis_backend]
    assert caches["default"] == {
        "BACKEND": expected_backend,
    }
