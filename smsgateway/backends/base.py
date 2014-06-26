import urllib2
import logging
import datetime
import re

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import get_callable

from smsgateway.enums import DIRECTION_OUTBOUND
from smsgateway.models import SMS
from smsgateway.sms import SMSRequest

logger = logging.getLogger(__name__)

try:
    hook = settings.SMSGATEWAY_HOOK
except:
    raise ImproperlyConfigured('No SMSGATEWAY_HOOK defined.')

class SMSBackend(object):
    def send(self, sms_request, account_dict):
        """
        Send an SMS message to one or more recipients, and create entries in the
        SMS table for each successful attempt.
        """
        capacity = self.get_url_capacity()
        sender = u'[%s]' % self.get_slug() if not sms_request.signature else sms_request.signature
        reference = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + u''.join(sms_request.to[:1])
        all_succeeded = True

        # Split SMSes into batches depending on the capacity
        requests = []
        while len(sms_request.to) > 0:
            requests.append(SMSRequest(
                sms_request.to[:capacity],
                sms_request.msg,
                sms_request.signature,
                reliable=sms_request.reliable,
                reference=reference
            ))
            del sms_request.to[:capacity]

        # Send each batch
        for request in requests:
            url = self.get_send_url(request, account_dict)
            logger.debug('Sending SMS using: %s' % url)

            # Make request to provider
            result = u''
            if url is not None:
                try:
                    sock = urllib2.urlopen(url)
                    result = sock.read()
                    sock.close()
                except:
                    return False
            logger.debug('Result: %s' % result)

            # Validate result, create log entry if successful
            if not self.validate_send_result(result):
                all_succeeded = False
            else:
                for dest in request.to:
                    SMS.objects.create(
                        sender=sender,
                        content=sms_request.msg,
                        to=dest,
                        backend=self.get_slug(),
                        direction=DIRECTION_OUTBOUND,
                        gateway_ref=reference
                    )

        return all_succeeded

    def get_send_url(self, sms_request, account_dict):
        """
        Returns the url to call to send text messages.
        """
        raise NotImplementedError

    def validate_send_result(self, result):
        """
        Returns whether sending an sms was successful.
        """
        raise NotImplementedError

    def handle_incoming(self, request, reply_using=None):
        """
        Django view to receive incoming SMSes
        """
        raise NotImplementedError

    def get_url_capacity(self):
        """
        Returns the number of text messages one call to the url can handle at once.
        """
        raise NotImplementedError

    def get_slug(self):
        """
        A unique short identifier for the SMS gateway provider.
        """
        raise NotImplementedError

    def process_incoming(self, request, sms):
        """
        Process an incoming SMS message and call the correct hook.
        """

        sms.save()

        # work with uppercase and single spaces
        content = sms.content.upper().strip()
        content = re.sub('\s+', " ", content)


        for keyword, subkeywords in hook.iteritems():
            if content[:len(keyword)] == unicode(keyword):
                subkeyword = content[len(keyword):].strip().split(u' ')[0].strip()
                if not subkeyword in subkeywords:
                    subkeyword = '*'
                if subkeyword in subkeywords:
                    try:
                        callable_hook = get_callable(subkeywords[subkeyword])
                    except ImportError:
                        raise ImproperlyConfigured(u'The function for %s was not found in the SMSGATEWAY_HOOK setting.' % subkeywords[subkeyword])
                    else:
                        return callable_hook(request, sms)
                return None

