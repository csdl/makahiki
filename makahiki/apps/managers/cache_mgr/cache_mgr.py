"""Provides utility methods for invalidating various caches."""

from django.core.cache import cache
import hashlib
from django.utils.http import urlquote


def info():
    """return the information about this cache."""
    return "%s" % type(cache)


def delete(key, version=None):
    """proxy the call to django cache.delete."""
    cache.delete(key, version)


def get_cache(key, default=None, version=None):
    """proxy the call to django cache.get."""
    value = cache.get(key, default, version)
    return value


def set_cache(key, value, timeout=None, version=None):
    """proxy the call to django cache.set."""
    cache.set(key, value, timeout, version)


def clear():
    """proxy the call to django cache.clear."""
    cache.clear()


def invalidate_template_cache(fragment_name, *variables):
    """Invalidates the cache associated with a template.
    Credit: `djangosnippets.org/snippets/1593/ <http://djangosnippets.org/snippets/1593/>`_"""

    args = hashlib.md5(u':'.join([urlquote(var) for var in variables]))
    cache_key = 'template.cache.%s.%s' % (fragment_name, args.hexdigest())
    delete(cache_key)
