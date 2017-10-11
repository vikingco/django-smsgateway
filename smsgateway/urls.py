from __future__ import absolute_import
from django.conf.urls import url

from smsgateway.views import backend_debug, backend_handle_incoming

urlpatterns = [
    url(r'^backend/debug/$', backend_debug, name='smsgateway_backend_debug'),
    url(r'^(?P<backend_name>.+)/incoming/$', backend_handle_incoming, name='smsgateway_backend'),
]
