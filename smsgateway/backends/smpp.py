#-*- coding: utf-8 -*-

import datetime
import logging
import socket

from smsgateway.backends.base import SMSBackend
from smsgateway.enums import DIRECTION_OUTBOUND
from smsgateway.models import SMS
from smsgateway.smpplib import client
from smsgateway.smpplib.smpp import make_pdu
from smsgateway.sms import SMSRequest

logger = logging.getLogger(__name__)


# SMSGATEWAY_ACCOUNTS['smpp'] ==
        # 'backend': 'smpp',
        # 'host': 'localhost',
        # 'port': '2775',
        # 'system_id': 'smppclient1',
        # 'password': 'pwd1',
        # 'system_type': 'www',

class SMPPBackend(SMSBackend):

    def __init__(self):
        self.client = None
        self.sms_list = None
        self.sender = None
        self.sms_data_iter = None
        self.sent_smses = []


    def _initialize(self, sms_request, account_dict):
        sms_list = self._get_sms_list(sms_request)
        if not len(sms_list):
            logger.error("Nothing to send. sms_request: %s" % sms_request)
            return False

        if sms_request.signature:
            self.sender = sms_request.signature
        else: self.sender = u'[%s]' % self.get_slug()

        self.sms_data_iter = SMSDataIterator(sms_list)
        return True


    def _get_sms_list(self, sms_request):
        if not sms_request:
            return []
        sms_list = []
        reference = (datetime.datetime.now().strftime('%Y%m%d%H%M%S') 
                     + u''.join(sms_request.to[:1]))
        for msisdn in sms_request.to:
            sms_list.append(SMSRequest(msisdn, 
                                       sms_request.msg, 
                                       sms_request.signature, 
                                       reliable=sms_request.reliable,
                                       reference=reference))
        return sms_list


    def _connect(self, conf):
        self.client = client.Client(conf['host'], conf['port']) 
        self.client.connect()
        logger.debug("Connecting to SMSC '%(host)s:%(port)s', "
                     "System ID '%(system_id)s', "
                     "System Type '%(system_type)s'" % conf)
        self.client.set_message_received_handler(self._send_recv_loop)
        try:
            self.client.bind_transceiver(**conf)
        except:
            self.client.disconnect()


    def _disconnect(self):
        self.client.unbind()
        self.client.disconnect()


    def _send_recv_loop(self, **kwargs):
        if (not kwargs.get('pdu', False) or 
            kwargs['pdu'].command != 'deliver_sm'):
            raise Exception('deliver_sm PDU expected')
        try:
            instance_data = self.sent_smses.pop(0)
            SMS.objects.create(**instance_data)
        except IndexError:
            logger.exception('Sent SMS List empty')
        try:
            sms_data = self.sms_data_iter.next()
        except StopIteration:
            return False
        else:
            self._send_sms(sms_data)
            return True


    def _send_sms(self, sms_data):
        source_sms = sms_data.pop('source_sms')
        resp = self.client.send_message(**sms_data)
        if not resp.is_error() and resp.is_response():
            sent_sms = {
                'sender': self.sender, 
                'to': sms_data['destination_addr'],
                'content': source_sms.msg,
                'backend': self.get_slug(),
                'direction': DIRECTION_OUTBOUND,
                'gateway_ref': source_sms.reference
            }
            self.sent_smses.append(sent_sms)

                
    def send(self, sms_request, account_dict):
        """SMPPBackend instances' entry point"""
        self._initialize(sms_request, account_dict)
        sms_data = self.sms_data_iter.next()
        self._connect(account_dict)
        self._send_sms(sms_data)
        self.client.listen()          
        self._disconnect()
        return True


    def get_slug(self):
        return 'smpp'


class SMSDataIterator:
    def __init__(self, sms_list):
        self.sms_list = sms_list

    def __iter__(self):
        return self

    def next(self):
        while len(self.sms_list):
            sms = self.sms_list.pop(0)
            text = sms.msg
            text = text.replace(u'€', u'EUR')
            text = text.encode('iso-8859-1', 'replace')
            
            return {
                'source_addr_ton': 0, 
                'source_addr': 0,
                'dest_addr_ton': 0, 
                'destination_addr': sms.to[0], # only one msisdn at this point
                'short_message': text,
                'source_sms': sms
             }
        raise StopIteration
