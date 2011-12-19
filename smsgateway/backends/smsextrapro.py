from django.http import HttpResponse
from django.conf import settings
from django.utils.http import urlencode


from smsgateway.models import SMS
from smsgateway.backends.base import SMSBackend
from smsgateway.utils import check_cell_phone_number
from smsgateway.sms import SMSRequest

import datetime

class SmsExtraProBackend(SMSBackend):
    def get_send_url(self, sms_request, account_dict):
        path = 'www.smsextrapro.com/HttpSend/HttpSend.php'
        username = account_dict['username']
        password = account_dict['password']
        msisdn = ';'.join([x[1:] for x in sms_request.to])
        signature = sms_request.signature[:11]

        # remove numbers
        signature = ''.join(c for c in signature if c not in '0123456789')

        msg = sms_request.msg

        try:
            msg = msg.encode('latin-1')
        except:
            pass

        context = {'Login': username,
                   'Psw': password,
                   'DestNum': msisdn,
                   'Signature': signature,
                   'Message': msg}

        querystring = urlencode(context)

        return 'http://%(path)s?%(querystring)s' % locals()

    def validate_send_result(self, result):
        return 'Ok' in result

    def handle_incoming(self, request, reply_using=None):
        return HttpResponse('')

    def get_slug(self):
        return 'smsextrapro'

    def get_url_capacity(self):
        return 20
