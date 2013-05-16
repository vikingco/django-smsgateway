#-*- coding: utf-8 -*-

import hashlib
import redis 

from django.conf import settings
from django.test import TestCase as DjangoTestCase

from smsgateway import send
from smsgateway.backends.redistore import RedistoreBackend
from smsgateway.models import SMS
from smsgateway.sms import SMSRequest
from smsgateway.utils import check_cell_phone_number, truncate_sms


req_data = {
    'to': '+32000000001;+32000000002;+32000000003',
    'msg': 'text of the message',
    'signature': 'cropped to 11 chars' 
}


class RedistoreBackendTestCase(DjangoTestCase):
    def setUp(self):
        self.backend = RedistoreBackend()
        self.conf = settings.SMSGATEWAY_ACCOUNTS['redistore']

    def test_init(self):
        for key in ['redis_key_prefix', 'redis_pool', 'redis_conn',
                    'reference', 'sender', 'sms_data_iter', 'sent_smses']:
            self.assert_(key in self.backend.__dict__.keys())

    def test_initialize_without_sms_request(self):
        self.assert_(self.backend._initialize(None, self.conf) == False)
        
    def test_initialize_with_sms_request(self):
        sms_request = SMSRequest(**req_data)
        self.assert_(self.backend._initialize(sms_request, self.conf) == True)

    def test_get_sms_list(self):
        sms_list = self.backend._get_sms_list(SMSRequest(**req_data))
        self.assert_(len(sms_list) == 3)
        for to, sms in zip(req_data['to'].split(';'), sms_list):
            self.assert_(sms.to[0] == check_cell_phone_number(to))
            self.assert_(sms.msg == truncate_sms(req_data['msg']))
            self.assertEqual(sms.signature,
                             req_data['signature'][:len(sms.signature)])


class RedistoreSendSingleSMSTestCase(DjangoTestCase):
    def setUp(self):
        self.conf = settings.SMSGATEWAY_ACCOUNTS['redistore']
        self.rdb = redis.Redis(host=self.conf['host'], 
                               port=self.conf['port'],
                               db=self.conf['dbn'])
        self.assert_(SMS.objects.count() == 0)
        send('+32000000001', 'testing message', 'the signature', 
             using='redistore') 
        self.assert_(SMS.objects.count() == 1)
        self.sms = SMS.objects.get(pk=1)

    def tearDown(self):
        for key in self.rdb.keys('%s*' % self.conf['key_prefix']):
            self.rdb.delete(key)
        self.assert_(len(self.rdb.keys('%s*' % self.conf['key_prefix'])) == 0)
        SMS.objects.all().delete()

    def test_single_sms_object_values(self):
        self.assert_(self.sms.content == 'testing message')
        self.assert_(self.sms.to == '+32000000001')
        self.assert_(self.sms.sender == 'the signature'[:len(self.sms.sender)])

    def test_redis_keys(self):
        key = hashlib.md5(self.sms.gateway_ref).hexdigest()
        queue_key = '%ssmsreq:%s' % (self.conf['key_prefix'], key)
        allqueues_key = '%soutq' % self.conf['key_prefix']
        sms_key = '%ssms:%s:0' % (self.conf['key_prefix'], key)
        self.assertTrue(self.rdb.exists(queue_key))
        self.assertTrue(self.rdb.exists(allqueues_key))
        self.assertTrue(self.rdb.exists(sms_key))
        self.assert_(self.rdb.llen(allqueues_key) == 1)
        self.assert_(self.rdb.lpop(allqueues_key) == queue_key)
        self.assert_(self.rdb.llen(queue_key) == 1)
        self.assert_(self.rdb.lpop(queue_key) == sms_key)
        something = self.rdb.hgetall(sms_key)
        self.assertEqual(
            self.rdb.hgetall(sms_key), {
                'source_addr_ton': '0',
                'source_addr': '15185',
                'dest_addr_ton': '1',
                'destination_addr': '+32000000001',
                'esme_vrfy_seqn': '-1',
                'short_message': 'testing message'})


class RedistoreSendMultipleSMSTestCase(DjangoTestCase):
    def setUp(self):
        self.conf = settings.SMSGATEWAY_ACCOUNTS['redistore']
        self.rdb = redis.Redis(host=self.conf['host'], 
                               port=self.conf['port'],
                               db=self.conf['dbn'])
        self.assert_(SMS.objects.count() == 0)
        send(req_data['to'], req_data['msg'], req_data['signature'],
             using='redistore') 
        self.assert_(SMS.objects.count() == 3)
        self.smses = SMS.objects.all()

    def tearDown(self):
        for key in self.rdb.keys('%s*' % self.conf['key_prefix']):
            self.rdb.delete(key)
        self.assert_(len(self.rdb.keys('%s*' % self.conf['key_prefix'])) == 0)
        SMS.objects.all().delete()

    def test_multiple_sms_object_values(self):
        for to, sms in zip (req_data['to'].split(';'), self.smses):
            self.assert_(sms.to == check_cell_phone_number(to))
            self.assert_(sms.content == truncate_sms(req_data['msg']))
            self.assertEqual(sms.sender,
                             req_data['signature'][:len(sms.sender)])
            self.assert_(sms.backend == 'redistore')
