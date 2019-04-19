from __future__ import absolute_import
__version__ = '2.1.19'


def get_account(using=None):
    from django.conf import settings
    accounts = settings.SMSGATEWAY_ACCOUNTS
    if using is not None:
        return accounts[using]
    else:
        return accounts[accounts['__default__']]


def send(to, msg, signature, using=None, reliable=False):
    """
    Send an SMS message immediately.

    *   'to' is a semicolon separated list of phone numbers with an international
        prefix (+32... etc).
    *   'msg' is the message itself as a unicode object (max 160 characters).
    *   'signature' is where the message comes from. Depends on the backend in use.
    *   'using' is an optional parameter where you can specify a specific account
        to send messages from.
    """
    # Don't send empty smses
    if not msg:
        return

    from smsgateway.backends import get_backend
    from smsgateway.sms import SMSRequest
    account_dict = get_account(using)
    backend = get_backend(account_dict['backend'])
    sms_request = SMSRequest(to, msg, signature, reliable=reliable)
    return backend.send(sms_request, account_dict)


def send_queued(to, msg, signature, using=None, reliable=False, priority=None):
    """
    Place SMS message in queue to be sent.
    """
    # Don't send empty smses
    if not msg:
        return

    from smsgateway.models import QueuedSMS
    queued_sms = QueuedSMS(
        to=to,
        content=msg,
        signature=signature,
        using=using if using is not None else '__none__',
        reliable=reliable
    )
    if priority is not None:
        queued_sms.priority = priority
    queued_sms.save()
