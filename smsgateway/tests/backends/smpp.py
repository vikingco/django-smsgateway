#-*- coding: utf-8 -*-

import os
import sys

from django.conf import settings
from django.test import TestCase as DjangoTestCase
from smsgateway import send
from smsgateway.backends.smpp import SMPPBackend
from smsgateway.models import SMS
from smsgateway.sms import SMSRequest
from smsgateway.utils import check_cell_phone_number, truncate_sms
from smsgateway.smpplib.client import (SMPP_CLIENT_STATE_CLOSED,
                                       SMPP_CLIENT_STATE_OPEN,
                                       SMPP_CLIENT_STATE_BOUND_TX,
                                       SMPP_CLIENT_STATE_BOUND_RX,
                                       SMPP_CLIENT_STATE_BOUND_TRX)


req_data = {
    'to': '+32000000001;+32000000002;+32000000003',
    'msg': 'text of the message',
    'signature': 'cropped to 11 chars' 
}


class SMPPBackendTestCase(DjangoTestCase):
    def setUp(self):
        self.backend = SMPPBackend()

    def test_init(self):
        for key in ['client', 'sender', 'sms_data_iter', 'sent_smses']:
            self.assert_(key in self.backend.__dict__.keys())

    def test_initialize_without_sms_request(self):
        self.assert_(self.backend._initialize(None) == False)

    def test_initialize_with_sms_request(self):
        sms_request = SMSRequest(**req_data)
        self.assert_(self.backend._initialize(sms_request) == True)

    def test_get_sms_list(self):
        sms_list = self.backend._get_sms_list(SMSRequest(**req_data))
        self.assert_(len(sms_list) == 3)
        for to, sms in zip(req_data['to'].split(';'), sms_list):
            self.assert_(sms.to[0] == check_cell_phone_number(to))
            self.assert_(sms.msg == truncate_sms(req_data['msg']))
            self.assertEqual(sms.signature,
                             req_data['signature'][:len(sms.signature)])

    def test_connect(self):
        self.assert_(self.backend.client == None)
        account_dict = settings.SMSGATEWAY_ACCOUNTS['smpp']
        self.backend._connect(account_dict)
        self.assert_(self.backend.client != None)
        self.assert_(self.backend.client.receiver_mode == True)
        self.assert_(self.backend.client.state == SMPP_CLIENT_STATE_BOUND_TRX)

    def test_connect_when_bind_fails(self):
        from mock import patch
        from smsgateway.smpplib.client import Client
        self.assert_(self.backend.client == None)
        patcher = patch.object(Client, 'bind_transceiver') 
        account_dict = settings.SMSGATEWAY_ACCOUNTS['smpp']
        with patcher as raise_exception:
            raise_exception.side_effect = Exception('Meeeck')
            self.backend._connect(account_dict)
        self.assert_(self.backend.client != None)
        self.assert_(self.backend.client.receiver_mode == False)
        self.assert_(self.backend.client.state == SMPP_CLIENT_STATE_CLOSED)


class SMPPBackendSendTestCase(DjangoTestCase):
    def test_send_single_sms(self):
        self.assert_(SMS.objects.count() == 0)
        send('+32000000001', 'testing message', 'the signature', using='smpp') 
        self.assert_(SMS.objects.count() == 1)
        sms = SMS.objects.get(pk=1)
        self.assert_(sms.content == 'testing message')
        self.assert_(sms.to == '+32000000001')
        self.assert_(sms.sender == 'the signature'[:len(sms.sender)])

    def test_send_multiple_separated_sms(self):
        self.assert_(SMS.objects.count() == 0)
        send(req_data['to'], req_data['msg'], req_data['signature'], 
             using='smpp') 
        self.assert_(SMS.objects.count() == 3)
        smses = SMS.objects.all()
        for to, sms in zip (req_data['to'].split(';'), smses):
            self.assert_(sms.to == check_cell_phone_number(to))
            self.assert_(sms.content == truncate_sms(req_data['msg']))
            self.assertEqual(sms.sender,
                             req_data['signature'][:len(sms.sender)])
            self.assert_(sms.backend == 'smpp')

