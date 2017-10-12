# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from logging import getLogger

from django.template import Context, Template
from requests import post, exceptions, codes
from xmltodict import parse

from smsgateway.backends.base import SMSBackend
from smsgateway.enums import DIRECTION_OUTBOUND
from smsgateway.models import SMS
from smsgateway.search_dict import SearchDict
from smsgateway.sms import SMSRequest


logger = getLogger(__name__)


class TransatelBackend(SMSBackend):
    """Implementation of Transatel SOAP API backend"""

    TEMPLATE = """<soapenv:Envelope
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:ser="http://service-api.transatel.com/">
        <soapenv:Header/>
        <soapenv:Body>
            <ser:SendSMS>
                <ser:TransactionId>{{ transaction_id }}</ser:TransactionId>
                <ser:ClientLogin>{{ login }}</ser:ClientLogin>
                <ser:ClientPwd>{{ password }}</ser:ClientPwd>
                <ser:Profile></ser:Profile>
                <ser:AuditUserName></ser:AuditUserName>
                <ser:Msisdn>{{ msisdn }}</ser:Msisdn>
                <ser:ServiceName>{{ service_name }}</ser:ServiceName>
                <ser:MessageType>sms_txt_latin1</ser:MessageType>
                <ser:Message>{{ msg }}</ser:Message>
          </ser:SendSMS>
       </soapenv:Body>
    </soapenv:Envelope>
    """

    def __init__(self, template=None):
        super(SMSBackend, self).__init__()

        self.template = template or self.TEMPLATE

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
        while sms_request.to:
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
            if not url:
                return False

            xml = self._xml_for_request(request, account_dict)
            headers = self._headers_for_xml(xml)

            try:
                response = post(url, data=xml, headers=headers)
            except exceptions.ConnectionError:
                logger.warning('Connection error')
                return False
            except exceptions.Timeout:
                logger.warning('Connection timed out')
                return False
            except Exception:
                logger.warning('Something else went wrong')
                return False

            if not response.status_code == codes.ok:
                logger.warning('Wrong status code for transatel SMS call')
                return False

            # Validate result, create log entry if successful
            if not self.validate_send_result(response.content):
                all_succeeded = False
            else:
                for dest in request.to:
                    SMS.objects.create(
                        sender=sender,
                        content=sms_request.msg,
                        to=dest,
                        backend=self.get_slug(),
                        direction=DIRECTION_OUTBOUND,
                        gateway_ref=self.get_gateway_ref(reference, response.content)
                    )

        return all_succeeded

    def _xml_for_request(self, request, account_dict):
        """Generate the XML for an SMS request"""
        return Template(self.template).render(
            Context({
                'transaction_id': self.get_send_reference(request),
                'login': account_dict['username'],
                'password': account_dict['password'],
                'msisdn': request.to[0],
                'msg': request.msg,
                'service_name': account_dict['servicename'],
            })
        )

    @staticmethod
    def _headers_for_xml(xml):
        """Generate headers for xml"""
        return {'Content-Type': 'text/xml; charset=utf-8', 'Content-Length': str(len(xml))}

    def get_send_url(self, sms_request, account_dict):
        """Transatel uses SOAP, so just use the root here."""
        return account_dict['url']

    @staticmethod
    def _validate_result_xml(search_dict, validation_element='ns2:result', valid_result_codes=None):
        """Parse XML and check the status code"""
        valid_result_codes = valid_result_codes or ('0',)
        if search_dict.find(validation_element) not in valid_result_codes:
            logger.warning('Invalid result status with for transatel SMS')
            return False
        return True

    def validate_send_result(self, result):
        result = parse(result, dict_constructor=SearchDict)
        return self._validate_result_xml(result)

    @staticmethod
    def _get_transaction_id(search_dict, transaction_id_element='ns2:transactionId'):
        """Get transaction ID from transatel search dict response"""
        return search_dict.find(transaction_id_element)

    def get_gateway_ref(self, reference, result=None):
        result = parse(result, dict_constructor=SearchDict)
        return self._get_transaction_id(result) or reference

    def handle_incoming(self, request, reply_using=None):
        raise NotImplementedError()

    def get_slug(self):
        return 'transatel'

    def get_url_capacity(self):
        return 1
