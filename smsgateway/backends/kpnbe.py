# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.conf import settings
from django.utils.http import urlencode

from gargoyle import gargoyle

from smsgateway.backends.base import SMSBackend


class KPNBEBackend(SMSBackend):
    def get_slug(self):
        return 'kpnbe'

    def handle_incoming(self, request, reply_using=None):
        return HttpResponse('')

    def get_url_capacity(self):
        return 1

    def validate_send_result(self, result):
        return True

    def get_send_url(self, sms_request, account_dict):
        # Get correct url to use
        if 'endpoint' in account_dict:
            endpoint = account_dict['endpoint']
        else:
            url = 'secondary' if gargoyle.is_active('smsgateway-kpn-use-secondary-url') else 'primary'
            endpoint = settings.SMSGATEWAY_KPNBE_URLS[url] + account_dict['username']

        # Encode message
        msg = sms_request.msg
        msg = msg.replace(u'€', u'EUR')
        try:
            msg = msg.encode('iso-8859-1', 'replace')
        except:
            pass

        querystring = urlencode({
            'username': account_dict['username'],
            'password': account_dict['password'],
            'mobile_no': ','.join([x[1:] for x in sms_request.to]),
            'origin_addr': account_dict.get('signature', '8210'),
            'msg': msg,
            'msgtype': 'ISO-8859-1'
        })
        return '{}?{}'.format(endpoint, querystring)
