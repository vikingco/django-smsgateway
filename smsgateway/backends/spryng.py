# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.conf import settings
from django.utils.http import urlencode

from smsgateway.models import SMS
from smsgateway.backends.base import SMSBackend
from smsgateway.utils import check_cell_phone_number
from smsgateway.sms import SMSRequest

import datetime

class SpryngBackendOld(SMSBackend):
    def get_send_url(self, sms_request, account_dict):
        path = 'www.spryng.nl/SyncTextService'
        username = account_dict['username']
        password = account_dict['password']
        smstype = account_dict.get('SMSTYPE', 'ECONOMIC')

        # override smstype, we want in this case a guaranteed delivery
        if sms_request.reliable:
            smstype = 'BUSINESS'

        msisdn = ','.join([x[1:] for x in sms_request.to])
        signature = sms_request.signature

        msg = sms_request.msg

        try:
            msg = msg.encode('latin-1')
        except:
            pass

        context = {'OPERATION': 'send',
                   'USERNAME': username,
                   'PASSWORD': password,
                   'DESTINATION': msisdn,
                   'SENDER': signature,
                   'BODY': msg,
                   'SMSTYPE': smstype}

        querystring = urlencode(context)

        return 'https://%(path)s?%(querystring)s' % locals()

    def validate_send_result(self, result):
        return '01' in result

    def handle_incoming(self, request, reply_using=None):
        return HttpResponse('')

    def get_slug(self):
        return 'spryng_old'

    def get_url_capacity(self):
        return 20

class SpryngBackend(SMSBackend):
    def get_slug(self):
        return 'spryng'

    def handle_incoming(self, request, reply_using=None):
        return HttpResponse('')

    def get_url_capacity(self):
        return 1

    def validate_send_result(self, result):
        return result == u'1'

    def get_send_url(self, sms_request, account_dict):
        path = 'www.spryng.nl/send.php'
        username = account_dict['username']
        password = account_dict['password']
        smstype = account_dict.get('SMSTYPE', 'BUSINESS') # or 'ECONOMIC'

        msisdn = ','.join([x[1:] for x in sms_request.to])
        signature = sms_request.signature

        msg = sms_request.msg
        msg = msg.replace(u'€', unichr(128))

        try:
            msg = msg.encode('iso-8859-15')
            #msg = msg.encode('latin-1')
        except:
            pass

        context = {'REFERENCE': sms_request.reference or '',
                   'USERNAME': username,
                   'PASSWORD': password,
                   'DESTINATION': msisdn,
                   'SENDER': signature,
                   'BODY': msg,
                   'SERVICE': 'smsgateway',
                   'ROUTE': smstype,
                   'ALLOWLONG': '0'}

        querystring = urlencode(context)

        return 'https://%(path)s?%(querystring)s' % locals()
