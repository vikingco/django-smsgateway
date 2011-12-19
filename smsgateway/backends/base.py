from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import get_callable

from smsgateway.models import *
from smsgateway.sms import SMSRequest

import urllib2
import logging
import datetime

logger = logging.getLogger('sms-errors')

try:
    hook = settings.SMSGATEWAY_HOOK
except:
    raise ImproperlyConfigured(u'Please define a SMSGATEWAY_HOOK setting with a string containing the full path to a function. The function must accept smsgateway.models.SMS object and the current request and must return a response string or None.')


class SMSBackend(object):
    def send(self, sms_request, account_dict):
        requests = []
        capacity = self.get_url_capacity()
        sender = u'[%s]' % self.get_slug() if not sms_request.signature else sms_request.signature
        
        reference = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + u''.join(sms_request.to[:1])
        
        while len(sms_request.to) > 0:
            requests.append(SMSRequest(sms_request.to[:capacity], sms_request.msg, sms_request.signature, reliable=sms_request.reliable, reference=reference))
            del sms_request.to[:capacity]

        ok = True
        for request in requests:
            url = self.get_send_url(request, account_dict)
            if settings.DEBUG:
                print('Sending SMS using:')
                print(url)

            result = u''
            if url is not None:
                try:
                    sock = urllib2.urlopen(url)
                    result = sock.read()
                    sock.close()
                except:
                    return False

            if settings.DEBUG:
                print('Result:')
                print(result)
            if not self.validate_send_result(result):
                ok = False
            else:
                for dest in request.to:
                    SMS.objects.create(sender=sender, content=sms_request.msg, to=dest, backend=self.get_slug(), direction=DIRECTION_OUTBOUND, gateway_ref=reference)

        return ok

    def get_send_url(self, sms_request, account_dict):
        '''
        Returns the url to call to send text messages.
        'sms_request' is a smsgateway.sms.SMSRequest object
        'using' is a dictionary containing the 'backend' and, when appropriate, a 'username' and 'password'.

        You can also implement other functionality here. When a URL is not needed, just return None.
        '''

        raise NotImplementedError

    def validate_send_result(self, result):
        '''
        This function returns True when sending an sms was successful.
        '''
        raise NotImplementedError

    def handle_incoming(self, request, reply_using=None):
        '''
        This is a django view. Map this to the right URL where you are
        expecting incoming messages from this gateway.

        You can specify the reply_using keyword argument, this is an account
        specified in SMSGATEWAY_ACCOUNTS. When omitted, the default account
        will be used.
        '''
        raise NotImplementedError

    def get_url_capacity(self):
        '''
        Returns the number of text messages one ReST-call (url) can handle at once.
        '''
        raise NotImplementedError

    def get_slug(self):
        '''
        A unique short identifier for the SMS gateway provider.
        For example: mobileweb, zong, smsextrapro, spryng, ...
        '''
        raise NotImplementedError

    def process_incoming(self, request, sms):
        '''
        This method must be called from the handle_incoming implementation.

        The 'request' parameter is provided via the handle_incoming view so
        you only have to pass it on.
        The 'sms' parameter should be an unsaved SMS model instance.

        When the return value of this function is not None, it should be sent
        as a reply to the incoming message.
        '''
        sms.save()

        # make sure the content of the sms is uppercase and has its spaces stripped
        content = sms.content.upper().strip()

        for keyword, subkeywords in hook.iteritems():
            if content[:len(keyword)] == unicode(keyword):
                subkeyword = content[len(keyword):].strip().split(u' ')[0].strip()
                if not subkeyword in subkeywords: 
                    subkeyword = '*'
                if subkeyword in subkeywords:
                    try:
                        callable_hook = get_callable(subkeywords[subkeyword])
                    except ImportError:
                        raise ImproperlyConfigured(u'Please correct the SMSGATEWAY_HOOK setting. The function at %s was not found.' % subkeywords[subkeyword])
                    else:
                        return callable_hook(request, sms)
                break
        return None

