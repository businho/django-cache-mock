import pytest
from django.conf import settings
from django.core.cache import InvalidCacheBackendError, caches

from django_cache_mock.exceptions import LazyLibImportError
from tests.thread_with_exceptions import Thread


def test_get_with_default_value(cache_alias_installed):
    cache = caches[cache_alias_installed]
    assert cache.get("FOO", default="BOO") == "BOO"


def _threaded_assert_value(cache_alias, key, expected_value):
    cache = caches[cache_alias]
    value = cache.get(key)
    assert value == expected_value


def test_different_threads_use_same_data(cache_alias_installed):
    cache_alias = cache_alias_installed
    cache = caches[cache_alias]
    key = "FOO"
    value = "BAR"
    cache.set(key, value)
    thread = Thread(target=_threaded_assert_value, args=(cache_alias, key, value))
    thread.start()
    thread.join()


def test_server_name(cache_alias_installed, tmp_path):
    cache_alias = cache_alias_installed
    location = str(tmp_path / cache_alias)
    settings.CACHES[cache_alias]["LOCATION"] = location
    try:
        del caches[cache_alias]
    except AttributeError:
        # Ignore if cache is not defined yet.
        pass
    cache = caches[cache_alias]
    assert cache.location == location

    cache.set("FOO", "BAR")
    assert cache.get("FOO") == "BAR"


def test_not_implemented_exception():
    try:
        1 / 0
    except ZeroDivisionError as _exc:

        class MyError(LazyLibImportError):
            exception = _exc

    with pytest.raises(MyError) as exception_info:
        MyError("server", params={})

    assert isinstance(exception_info.value, MyError)
    assert isinstance(exception_info.value.exception, ZeroDivisionError)


def test_redis_import_error(redis_cache_alias_not_installed):
    cache_alias = redis_cache_alias_not_installed
    try:
        caches[cache_alias]
    except LazyLibImportError:
        pass
    else:  # pragma: no cover
        pytest.fail("Cache unexpectedly worked.")


def test_memcached_import_error(memcached_cache_alias_not_installed):
    cache_alias = memcached_cache_alias_not_installed
    try:
        caches[cache_alias]
    except InvalidCacheBackendError:
        pass
    else:  # pragma: no cover
        pytest.fail("Cache unexpectedly worked.")
