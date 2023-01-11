import os

import pytest
from django.core.cache import caches


@pytest.fixture(scope="session", autouse=True)
def setup_env():
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.testapp.settings"


@pytest.fixture(
    scope="session",
    params=["default", "mockcache", "fakeredis", "redislite"],
)
def cache_alias(request):
    return os.getenv("CACHE_ALIAS", request.param)


@pytest.fixture(autouse=True)
def cache_cleanup(cache_alias):
    yield
    caches[cache_alias].clear()
