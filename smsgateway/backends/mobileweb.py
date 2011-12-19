from django.http import HttpResponse
from django.conf import settings
from django.utils.http import urlencode

import smsgateway
from smsgateway.models import SMS
from smsgateway.backends.base import SMSBackend
from smsgateway.utils import check_cell_phone_number
from smsgateway.sms import SMSRequest


import datetime
import re

class MobileWebBackend(SMSBackend):
    def get_send_url(self, sms_request, account_dict):
        path = 'gateway.mobileweb.be/smsin.asp'
        username = account_dict['username']
        password = account_dict['password']
        sid = account_dict['sid']

        msg = sms_request.msg
        to = sms_request.to[0][1:]
        try:
            msgcontent = urlencode({'msgcontent': msg.encode('latin-1')}) # This is a serious bug on the side of MobileWeb! This should be utf-8...
        except:
            msgcontent = urlencode({'msgcontent': msg})

        return u'http://%(path)s?logon=%(username)s&pass=%(password)s&gsmnr=%(to)s&%(msgcontent)s&sid=%(sid)s' % locals()

    def validate_send_result(self, result):
        return 'accepted' in result

    def handle_incoming(self, request, reply_using=None):
        if request.method == 'POST':
            request_dict = request.POST
        else:
            request_dict = request.GET

        if not 'SendDateTime' in request_dict:
            return HttpResponse('')

        timestamp = request_dict['SendDateTime']
        year, month, day, hour, minute, second, ms = map(int, re.findall(r'(\d+)', timestamp))
        timestamp = datetime.datetime(year, month, day, hour, minute, second)
        sms_dict = {'sent': timestamp,
                    'content': request_dict['MsgeContent'],
                    'sender': check_cell_phone_number(request_dict['SenderGSMNR']),
                    'to': request_dict['ShortCode'],
                    'operator': int(request_dict['Operator']),
                    'gateway_ref': request_dict['MessageID'],
                    'backend': self.get_slug(),
                    }
        
        # check simular text message
        if SMS.objects.filter(gateway_ref=request_dict['MessageID']).count() > 0:
            return HttpResponse('OK')
        
        sms = SMS(**sms_dict)
        response = self.process_incoming(request, sms)

        if response is not None:
            signature = smsgateway.get_account(reply_using)['reply_signature']
            smsgateway.send([sms.sender], response, signature, using=reply_using)
            return HttpResponse(response)
        return HttpResponse('OK')

    def get_slug(self):
        return 'mobileweb'

    def get_url_capacity(self):
        return 1
