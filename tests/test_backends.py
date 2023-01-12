import pytest
from django.core.cache import caches

from tests.thread_with_exceptions import Thread


@pytest.fixture(autouse=True)
def always_cleanup_cache_here(cache_cleanup):
    pass


def test_get_with_default_value(cache_alias):
    cache = caches[cache_alias]
    assert cache.get("FOO", default="BOO") == "BOO"


def _threaded_assert_value(cache_alias, key, expected_value):
    cache = caches[cache_alias]
    value = cache.get(key)
    assert value == expected_value


def test_different_threads_use_same_data(cache_alias):
    cache = caches[cache_alias]
    key = "FOO"
    value = "BAR"
    cache.set(key, value)
    thread = Thread(target=_threaded_assert_value, args=(cache_alias, key, value))
    thread.start()
    thread.join()
