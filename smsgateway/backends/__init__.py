from django.conf import settings
from django.core.urlresolvers import get_mod_func

REGISTRY = {}

backends = getattr(settings, 'SMSGATEWAY_BACKENDS', ('smsgateway.backends.mobileweb.MobileWebBackend',))

for entry in backends:
    module_name, class_name = get_mod_func(entry)
    backend_class = getattr(__import__(module_name, {}, {}, ['']), class_name)
    instance = backend_class()
    REGISTRY[instance.get_slug()] = instance

def get_backend(slug):
    return REGISTRY.get(slug, None)

# TODO: implement http://www.clickatell.com/developers/api_http.php