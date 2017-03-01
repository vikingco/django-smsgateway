# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.utils.http import urlencode
from django.conf import settings

from smsgateway.backends.base import SMSBackend


class SpryngBackend(SMSBackend):
    def get_send_url(self, sms_request, account_dict):
        # Encode message
        msg = sms_request.msg
        msg = msg.replace(u'€', unichr(128))
        try:
            msg = msg.encode('iso-8859-15')
        except:
            pass

        if isinstance(sms_request.to, basestring):
            sms_request.to = [sms_request.to]

        # Spryng doesn't accept the prefix '+'
        msisdn_prefix = getattr(settings, 'SMSGATEWAY_MSISDN_PREFIX', '')
        if msisdn_prefix:
            to_addresses = []
            for to in sms_request.to:
                if to.startswith(msisdn_prefix):
                    to = to[len(msisdn_prefix):]
                to_addresses.append(to)
            sms_request.to = to_addresses

        querystring = urlencode({
            'REFERENCE': sms_request.reference or '',
            'USERNAME': account_dict['username'],
            'PASSWORD': account_dict['password'],
            'DESTINATION': ','.join(sms_request.to),
            'SENDER': sms_request.signature,
            'BODY': msg,
            'SERVICE': 'smsgateway',
            'ROUTE': account_dict.get('SMSTYPE', 'BUSINESS'),
            'ALLOWLONG': '0',
        })
        return 'https://www.spryng.nl/send.php?{}'.format(querystring)

    def get_slug(self):
        return 'spryng'

    def handle_incoming(self, request, reply_using=None):
        return HttpResponse('')

    def get_url_capacity(self):
        return 1

    def validate_send_result(self, result):
        return result == u'1'
