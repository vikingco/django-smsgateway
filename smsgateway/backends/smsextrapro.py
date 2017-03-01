from django.http import HttpResponse
from django.utils.http import urlencode

from smsgateway.backends.base import SMSBackend


class SmsExtraProBackend(SMSBackend):
    def get_send_url(self, sms_request, account_dict):
        # Set signature
        signature = sms_request.signature[:11]
        signature = ''.join(c for c in signature if c not in '0123456789')

        # Encode message
        msg = sms_request.msg
        try:
            msg = msg.encode('latin-1')
        except:
            pass

        querystring = urlencode({
            'Login': account_dict['username'],
            'Psw': account_dict['password'],
            'DestNum': ';'.join([x[1:] for x in sms_request.to]),
            'Signature': signature,
            'Message': msg,
        })
        return 'http://www.smsextrapro.com/HttpSend/HttpSend.php?{}'.format(querystring)

    def validate_send_result(self, result):
        return 'Ok' in result

    def handle_incoming(self, request, reply_using=None):
        return HttpResponse('')

    def get_slug(self):
        return 'smsextrapro'

    def get_url_capacity(self):
        return 20
