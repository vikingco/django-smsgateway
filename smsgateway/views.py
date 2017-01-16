from django import forms
from django.http import Http404
from django.conf import settings
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.admin.views.decorators import staff_member_required

from smsgateway import send
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

    context.update({'form': form})
    return render_to_response(
        'smsgateway/backend_debug.html',
        context,
        context_instance=RequestContext(request)
    )


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
