# django-cache-mock

Use in-process mocks to avoid setting up external caches for Django during
development.

Django has a limited built-in `django.core.cache.backends.locmem.LocMemCache`,
to help development, but Django do some magic to always give you a working
connection.

I have some reasons to abuse Django cache this way:

* Thread safety: Django spin one connection per thread to avoid issues with
thread unsafe drivers.
* Good defaults: Django run connections with good defaults.
* Connection reuse: Django already have a pool running and in most cases it is
better to use it.

## Install

```shell
$ pip install django-cache-mock
```

Also, it is possible to install with the backends you want.

For `mockcache`, it installs a fork of the original package because it doesn´t
work for new versions of Python.

```shell
$ pip install django-cache-mock[mockcache]
$ pip install django-cache-mock[fakeredis]
$ pip install django-cache-mock[redislite]
```

## How to use

In your Django settings you already have `CACHES` defined.

For `memcached`, it's something like that:

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
        "LOCATION": os.getenv("MEMCACHED_HOSTS"),
        "OPTIONS": {
            "no_delay": True,
            "ignore_exc": True,
            "max_pool_size": 4,
            "use_pooling": True,
        },
    },
}
```

Just make a call to `django_cache_mock.patch` to replace with a mock backend.

**The lib will patch only when cache LOCATION is not defined.**

```python
import django_cache_mock

if DEBUG:  # Apply it only in debug mode to be extra careful.
    django_cache_mock.patch(CACHES, "default", "mockcache")
```

This patch replace cache with a mocked one. For mockcache,

## Custom cache options

The `patch` function accepts custom params. It can be used to override mock
behaviours, like the db file `redislite` will use, defined by `LOCATION`:

```python
django_cache_mock.patch(CACHES, "default", "redislite", {"LOCATION": "data/redis.db"})
```

## Redis backends

Redis has several options to run. This lib implements `fakeredis` and `redislite`,
with `django.core.cache` or `django-redis`.

By default, the lib try to maintain the same behavior of the original implementation.
If config uses `django-redis`, when you set use backend `fakeredis`, it will use
it as `fakeredis[django-redis]`.

```python
# Force to use django-redis. It is not necessary, the lib already try to use
# django-redis if cache uses `django_redis.cache.cache.RedisCache`.
django_cache_mock.patch(CACHES, "redis", "fakeredis[django-redis]")
django_cache_mock.patch(CACHES, "redis", "redislite[django-redis]")
```

## How to access connections

To get Django memcached and redis clients from cache:

```python
from django.core.cache import caches

def give_me_memcached():
    return caches["memcached"]._cache

# for django.core.cache.backends.redis
def give_me_primary_redis():
    return caches["redis"]._cache.get_client(write=True)

def give_me_secondary_redis():
    return caches["redis"]._cache.get_client()

# for django-redis
def give_me_primary_redis():
    return caches["redis"].client.get_client()

def give_me_secondary_redis():
    return caches["redis"].client.get_client(write=False)

# Yes, django and django-redis have different write flag defaults.
```
