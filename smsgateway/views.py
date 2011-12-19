from django.http import HttpResponse, Http404
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import get_callable
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.http import urlencode
from django.contrib.admin.views.decorators import staff_member_required

from smsgateway.utils import check_cell_phone_number, truncate_sms

from smsgateway.models import *
from smsgateway.backends import REGISTRY, get_backend
from smsgateway import send

import datetime
import re
import urllib2
import logging

logger = logging.getLogger('sms-errors')

hook = None

from django import forms

accounts = getattr(settings, 'SMSGATEWAY_ACCOUNTS', {})
class BackendDebugForm(forms.Form):
    account = forms.ChoiceField(choices=[(k, u'%s (using %s)' % (k, accounts[k]['backend'])) for k in accounts.keys() if k != '__default__'])
    recipients = forms.CharField(help_text=u'Separate multiple recipients with a semicolon (;).')
    message = forms.CharField(widget=forms.widgets.Textarea())
    signature = forms.CharField()

@staff_member_required
def backend_debug(request):
    context = {}

    if request.method == 'POST':
        form = BackendDebugForm(request.POST)

        if form.is_valid():
            if (send(form.cleaned_data['recipients'].split(';'), form.cleaned_data['message'], form.cleaned_data['signature'], form.cleaned_data['account'])):
                context.update({'message': u'Text message sent'})
            else:
                context.update({'message': u'Sending failed'})
    else:
        form = BackendDebugForm()

    context.update({'form': form})
    return render_to_response('smsgateway/backend_debug.html', context, context_instance=RequestContext(request))

def backend_handle_incoming(request, backend_name):
    '''Map to the backends handle_incoming method'''
    if backend_name == 'debug':
        return backend_debug(request)
    b = get_backend(backend_name)
    if b is None:
        raise Http404
    return b.handle_incoming(request)