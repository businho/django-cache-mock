import threading

from django.core.cache import caches


class _Thread(threading.Thread):
    def run(self):
        self.exc = None
        try:
            super().run()
        except BaseException as exc:
            self.exc = exc

    def join(self):
        threading.Thread.join(self)
        if self.exc:
            raise self.exc


def test_get_with_default_value(cache_alias):
    cache = caches[cache_alias]
    assert cache.get("FOO", default="BOO") == "BOO"


def _threaded_assert_value(cache_alias, key, expected_value):
    cache = caches[cache_alias]
    value = cache.get(key)
    assert value == expected_value


def test_differente_threads_use_same_data(cache_alias):
    cache = caches[cache_alias]
    key = "FOO"
    value = "BAR"
    cache.set(key, value)
    thread = _Thread(target=_threaded_assert_value, args=(cache_alias, key, value))
    thread.start()
    thread.join()
