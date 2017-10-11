from __future__ import absolute_import
from django import forms
from django.http import Http404
from django.conf import settings
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

from smsgateway import send, __version__
from smsgateway.backends import get_backend

accounts = getattr(settings, 'SMSGATEWAY_ACCOUNTS', {})


class BackendDebugForm(forms.Form):
    account = forms.ChoiceField(choices=[(k, k) for k in accounts.keys() if k != '__default__'])
    recipients = forms.CharField(help_text=u'Separate multiple recipients with a semicolon (;).')
    message = forms.CharField(widget=forms.widgets.Textarea())
    signature = forms.CharField()


@staff_member_required
def backend_debug(request):
    """
    A form to let you send an SMS for debugging purposes.
    """
    context = {}

    if request.method == 'POST':
        form = BackendDebugForm(request.POST)

        if form.is_valid():
            success = send(
                form.cleaned_data['recipients'].split(';'),
                form.cleaned_data['message'],
                form.cleaned_data['signature'],
                form.cleaned_data['account']
            )
            if success:
                context.update({'message': u'Text message sent'})
            else:
                context.update({'message': u'Sending failed'})
    else:
        form = BackendDebugForm()

    context.update({
        'form': form,
        'version': __version__,
    })
    return render(request, 'smsgateway/backend_debug.html', context)


def backend_handle_incoming(request, backend_name):
    """
    Call the backend's handle_incoming method.
    """
    if backend_name == 'debug':
        return backend_debug(request)
    b = get_backend(backend_name)
    if b is None:
        raise Http404
    return b.handle_incoming(request)
