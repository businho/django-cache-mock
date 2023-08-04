import importlib
import os

import pytest
from django.core.cache import caches

from tests.testapp.settings import CACHES


@pytest.fixture(scope="session", autouse=True)
def setup_env():
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.testapp.settings"


@pytest.fixture(params=CACHES.keys())
def cache_alias(request):
    return request.param


def _validate_backend_installed(cache_alias):
    # Import at root level trigger https://github.com/jazzband/django-redis/issues/638.
    from django_cache_mock.exceptions import LazyLibImportError

    backend_module, backend_class = CACHES[cache_alias]["BACKEND"].rsplit(".", 1)
    module = importlib.import_module(backend_module)
    backend = getattr(module, backend_class)
    if issubclass(backend, LazyLibImportError):
        return False

    return True


@pytest.fixture
def cache_alias_installed(cache_alias):
    if not _validate_backend_installed(cache_alias):
        pytest.skip(f"Cache {cache_alias} dependencies not installed.")

    yield cache_alias
    caches[cache_alias].clear()
    del caches[cache_alias]


@pytest.fixture
def cache_alias_not_installed(cache_alias):
    if _validate_backend_installed(cache_alias):
        pytest.skip(f"Cache {cache_alias} dependencies installed.")
    return cache_alias


@pytest.fixture(params=["fakeredis", "redislite"])
def redis_backend(request):
    return request.param
