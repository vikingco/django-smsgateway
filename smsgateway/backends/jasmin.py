import datetime

from django.http import HttpResponse
from django.utils.http import urlencode

import smsgateway
from smsgateway.models import SMS
from smsgateway.backends.base import SMSBackend
from smsgateway.utils import check_cell_phone_number


class JasminBackend(SMSBackend):
    def get_send_url(self, sms_request, account_dict):
        # Encode message
        msg = sms_request.msg
        try:
            msg = msg.encode('latin-1')
        except:
            pass

        querystring = urlencode({
            'username': account_dict['username'],
            'password': account_dict['password'],
            'from': account_dict['signature'],
            'to': sms_request.to[0],
            'content': msg,
            'coding': 3,  # latin-1
        })
        return u'%s?%s' % (account_dict['url'], querystring)

    def validate_send_result(self, result):
        return 'Success' in result

    def get_gateway_ref(self, reference, result):
        # Fetch the id Jasmin returned
        return result.split()[1].strip('"')

    def handle_incoming(self, request, reply_using=None):
        request_dict = request.POST if request.method == 'POST' else request.GET

        # Check whether we've got an id
        if 'id' not in request_dict:
            return HttpResponse('')

        # Check whether we've already received this message
        if SMS.objects.filter(gateway_ref=request_dict['id']).exists():
            return HttpResponse('ACK/Jasmin')

        # Parse and process message
        sms_dict = {
            'sent': datetime.datetime.now(),
            'content': request_dict['content'],
            'sender': check_cell_phone_number(request_dict['from']),
            'to': request_dict['to'],
            'gateway_ref': request_dict['id'],
            'backend': self.get_slug(),
        }
        sms = SMS(**sms_dict)
        response = self.process_incoming(request, sms)

        # If necessary, send response SMS
        if response is not None:
            signature = smsgateway.get_account(reply_using)['reply_signature']
            success = smsgateway.send([sms.sender], response, signature, using=reply_using)
            # Sending failed, queue SMS
            if not success:
                smsgateway.send_queued(sms.sender, response, signature, reply_using)

        return HttpResponse('ACK/Jasmin')

    def get_slug(self):
        return 'jasmin'

    def get_url_capacity(self):
        return 1
