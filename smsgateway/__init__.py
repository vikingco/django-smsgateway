VERSION = (1, 0, 0)


def get_version():
    if len(VERSION) > 3 and VERSION[3] != 'final':
        return '%s.%s.%s %s' % (VERSION[0], VERSION[1], VERSION[2], VERSION[3])
    else:
        return '%s.%s.%s' % (VERSION[0], VERSION[1], VERSION[2])


__version__ = get_version()

def get_account(using=None):
    from django.conf import settings
    accounts = settings.SMSGATEWAY_ACCOUNTS
    if using is not None:
        account_dict = accounts[using]
    else:
        account_dict = accounts[accounts['__default__']]
    return account_dict

def send(to, msg, signature, using=None, reliable=False):
    from smsgateway import backends
    from smsgateway.sms import SMSRequest
    '''
    Send a text message using the gateway(s) specified in settings.py.

    *   'to' is a semicolon separated list of phone numbers with an international
        prefix (+32... etc).
    *   'msg' is the message itself as a unicode object (max 160 characters).
    *   'signature' is where the message comes from. Depends on the backend in use.
    *   'using' is an optional parameter where you can specify a specific account
        to send messages from.
    '''
    account_dict = get_account(using)
    backend = backends.get_backend(account_dict['backend'])
    sms_request = SMSRequest(to, msg, signature, reliable=reliable)
    return backend.send(sms_request, account_dict)


def send_queued(to, msg, signature, using=None, reliable=False):
    from smsgateway.models import QueuedSMS
    """
    Place SMS message in queue to be send.
    """
    if using is None:
        using = '__none__'
    QueuedSMS.objects.create(to=to, content=msg, signature=signature,
                             using=using, reliable=reliable)
    return True
