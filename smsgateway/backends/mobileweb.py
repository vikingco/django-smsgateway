from datetime import datetime
from re import findall

from django.http import HttpResponse
from django.utils.http import urlencode

from smsgateway import get_account, send, send_queued
from smsgateway.models import SMS
from smsgateway.backends.base import SMSBackend
from smsgateway.utils import check_cell_phone_number


class MobileWebBackend(SMSBackend):
    def get_send_url(self, sms_request, account_dict):
        # Encode message
        msg = sms_request.msg
        try:
            msg = msg.encode('latin-1')
        except:
            pass

        querystring = urlencode({
            'login': account_dict['username'],
            'pass': account_dict['password'],
            'gsmnr': sms_request.to[0][1:],
            'sid': account_dict['sid'],
            'msgcontent': msg,
        })
        return u'http://gateway.mobileweb.be/smsin.asp?{}'.format(querystring)

    def validate_send_result(self, result):
        return 'accepted' in result

    def handle_incoming(self, request, reply_using=None):
        request_dict = request.POST if request.method == 'POST' else request.GET

        # Check whether we've gotten a SendDateTime
        if 'SendDateTime' not in request_dict:
            return HttpResponse('')

        # Check whether we've already received this message
        if SMS.objects.filter(gateway_ref=request_dict['MessageID']).exists():
            return HttpResponse('OK')

        # Parse and process message
        year, month, day, hour, minute, second, ms = map(int, findall(r'(\d+)', request_dict['SendDateTime']))
        sms_dict = {
            'sent': datetime(year, month, day, hour, minute, second),
            'content': request_dict['MsgeContent'],
            'sender': check_cell_phone_number(request_dict['SenderGSMNR']),
            'to': request_dict['ShortCode'],
            'operator': int(request_dict['Operator']),
            'gateway_ref': request_dict['MessageID'],
            'backend': self.get_slug(),
        }
        sms = SMS(**sms_dict)
        response = self.process_incoming(request, sms)

        # If necessary, send response SMS
        if response is not None:
            signature = get_account(reply_using)['reply_signature']
            success = send([sms.sender], response, signature, using=reply_using)
            # Sending failed, queue SMS
            if not success:
                send_queued(sms.sender, response, signature, reply_using)
            return HttpResponse(response)

        return HttpResponse('OK')

    def get_slug(self):
        return 'mobileweb'

    def get_url_capacity(self):
        return 1
