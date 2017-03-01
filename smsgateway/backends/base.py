from urllib2 import urlopen
from logging import getLogger
from datetime import datetime
from re import sub

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import get_callable

from smsgateway.enums import DIRECTION_OUTBOUND
from smsgateway.models import SMS
from smsgateway.sms import SMSRequest

logger = getLogger(__name__)

try:
    all_hooks = settings.SMSGATEWAY_HOOK
except:
    raise ImproperlyConfigured('No SMSGATEWAY_HOOK defined.')


class SMSBackend(object):
    def send(self, sms_request, account_dict):
        """
        Send an SMS message to one or more recipients, and create entries in the
        SMS table for each successful attempt.
        """
        capacity = self.get_url_capacity()
        sender = u'[{}]'.format(self.get_slug()) if not sms_request.signature else sms_request.signature
        reference = self.get_send_reference(sms_request)
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

            # Make request to provider
            result = u''
            if url is not None:
                try:
                    sock = urlopen(url)
                    result = sock.read()
                    sock.close()
                except:
                    return False

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
                        gateway_ref=self.get_gateway_ref(reference, result)
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

    def get_send_reference(self, sms_request):
        """
        Generate a reference for the send sms
        """
        return datetime.now().strftime('%Y%m%d%H%M%S') + u''.join(sms_request.to[:1])

    def get_gateway_ref(self, reference, result=None):
        """
        Retrieve the gateway_ref, defaults to `reference`
        """
        return reference

    def _find_callable(self, content, hooks):
        """
        Parse the content of an sms according, and try to match it with a callable function defined in the settings.

        This function calls itself to dig through the hooks, because they can have an arbitrary depth.

        :param str content: the content of the sms to parse
        :param dict hooks: the hooks to match
        :returns str or None: the name of the function to call, or None if no function was matched
        """
        # Go throught the different hooks
        matched = False
        for keyword, hook in hooks.iteritems():
            # If the keyword of this hook matches
            if content.startswith(keyword + ' ') or content == keyword:
                matched = True
                break

        # If nothing matched, see whether there is a wildcard
        if not matched and '*' in hooks:
            hook = hooks['*']
            matched = True

        if matched:
            # Take off the first word
            remaining_content = content.split(' ', 1)[1] if ' ' in content else ''

            # There are multiple subkeywords, recurse
            if isinstance(hook, dict):
                return self._find_callable(remaining_content, hook)
            # This is the callable
            else:
                return hook

    def process_incoming(self, request, sms):
        """
        Process an incoming SMS message and call the correct hook.

        :param Request request: the request we're handling. Passed to the handler
        :param SMS sms: the sms we're processing
        :returns: the result of the callable function, or None if nothing was called
        """
        sms.save()

        # work with uppercase and single spaces
        content = sms.content.upper().strip()
        content = sub('\s+', ' ', content)

        # Try to find the correct hook
        callable_name = self._find_callable(content, all_hooks)

        # If no hook matched, check for a fallback
        if not callable_name and hasattr(settings, 'SMSGATEWAY_FALLBACK_HOOK'):
            callable_name = settings.SMSGATEWAY_FALLBACK_HOOK

        if not callable_name:
            return

        callable_function = get_callable(callable_name)
        return callable_function(request, sms)
