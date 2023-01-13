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


@pytest.fixture
def cache_alias_installed(cache_alias):
    module_names = cache_alias.replace("]", "").split("[")
    for module_name in module_names:
        try:
            importlib.import_module(module_name)
        except ImportError:
            pytest.skip(f"Module {module_name} not installed.")

    yield cache_alias
    caches[cache_alias].clear()
    del caches[cache_alias]


@pytest.fixture
def cache_alias_not_installed(cache_alias):
    module_names = cache_alias.replace("]", "").split("[")
    for module_name in module_names:
        try:
            importlib.import_module(module_name)
        except ImportError:
            pass
        else:
            pytest.skip(f"Module {module_name} installed.")
    return cache_alias


@pytest.fixture
def memcached_cache_alias_not_installed(cache_alias_not_installed):
    cache_alias = cache_alias_not_installed
    if "memcached" not in CACHES[cache_alias]["BACKEND"]:
        pytest.skip(f"Module {cache_alias} is not a memcached backend.")
    return cache_alias


@pytest.fixture
def redis_cache_alias_not_installed(cache_alias_not_installed):
    cache_alias = cache_alias_not_installed
    if "redis" not in CACHES[cache_alias]["BACKEND"]:
        pytest.skip(f"Module {cache_alias} is not a redis backend.")
    return cache_alias


@pytest.fixture(params=["fakeredis", "redislite"])
def redis_backend(request):
    return request.param
