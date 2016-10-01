from __future__ import unicode_literals

import inspect

from django.conf import settings
from django.utils import six

from . import Error, Tags, Warning, register


@register(Tags.urls)
def check_url_config(app_configs, **kwargs):
    if getattr(settings, 'ROOT_URLCONF', None):
        from django.urls import get_resolver
        resolver = get_resolver()
        if inspect.ismethod(resolver.check):
            return resolver.check(**kwargs)
    return []


def check_resolver(resolver):
    """
    Recursively check the resolver.
    """
    check_method = getattr(resolver, 'check', None)
    resolve_method = getattr(resolver, 'resolve', None)
    reverse_method = getattr(resolver, 'reverser', None)
    if inspect.ismethod(check_method):
        return check_method()
    elif resolve_method is None and reverse_method is None:
        return get_warning_for_invalid_pattern(resolver)
    else:
        return []


def get_warning_for_invalid_pattern(pattern):
    """
    Return a list containing a warning that the pattern is invalid.

    describe_pattern() cannot be used here, because we cannot rely on the
    urlpattern having regex or name attributes.
    """
    if isinstance(pattern, six.string_types):
        hint = (
            "Try removing the string '{}'. The list of urlpatterns should not "
            "have a prefix string as the first element.".format(pattern)
        )
    elif isinstance(pattern, tuple):
        hint = "Try using url() instead of a tuple."
    else:
        hint = None

    return [Error(
        "Your URL pattern {!r} is invalid. Ensure that urlpatterns is a list "
        "of url() instances.".format(pattern),
        hint=hint,
        id="urls.E004",
    )]
