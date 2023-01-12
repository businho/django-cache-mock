from unittest.mock import sentinel

import pytest

from django_cache_mock import patch


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
