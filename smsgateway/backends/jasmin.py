from datetime import datetime

from urllib2 import urlopen
from django.http import HttpResponse
from django.utils.http import urlencode

from smsgateway import get_account, send, send_queued
from smsgateway.models import SMS
from smsgateway.backends.base import SMSBackend
from smsgateway.utils import check_cell_phone_number
from smsgateway.sms import JasminSMSRequest

from smsgateway.enums import DIRECTION_OUTBOUND


class JasminBackend(SMSBackend):

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
            requests.append(JasminSMSRequest(
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
        return u'{}?{}'.format(account_dict['url'], querystring)

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
            'sent': datetime.now(),
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
            signature = get_account(reply_using)['reply_signature']
            success = send([sms.sender], response, signature, using=reply_using)
            # Sending failed, queue SMS
            if not success:
                send_queued(sms.sender, response, signature, reply_using)

        return HttpResponse('ACK/Jasmin')

    def get_slug(self):
        return 'jasmin'

    def get_url_capacity(self):
        return 1
