from __future__ import absolute_import
from django.conf import settings
from smsgateway.utils import is_pre_django2
if is_pre_django2():
    from django.core.urlresolvers import get_mod_func
else:
    from django.urls import get_mod_func


REGISTRY = {}

backends = getattr(settings, 'SMSGATEWAY_BACKENDS', ())

for entry in backends:
    module_name, class_name = get_mod_func(entry)
    backend_class = getattr(__import__(module_name, {}, {}, ['']), class_name)
    instance = backend_class()
    REGISTRY[instance.get_slug()] = instance


def get_backend(slug):
    return REGISTRY.get(slug, None)
