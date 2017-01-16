from django.test import TestCase as DjangoTestCase
from smsgateway.backends.smpp import SMPPBackend
from smsgateway.sms import SMSRequest
from smsgateway.utils import check_cell_phone_number, truncate_sms


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
            assert key in self.backend.__dict__.keys()

    def test_initialize_without_sms_request(self):
        assert self.backend._initialize(None) is False

    def test_initialize_with_sms_request(self):
        sms_request = SMSRequest(**req_data)
        assert self.backend._initialize(sms_request) is True

    def test_get_sms_list(self):
        sms_list = self.backend._get_sms_list(SMSRequest(**req_data))
        assert len(sms_list) == 3
        for to, sms in zip(req_data['to'].split(';'), sms_list):
            assert sms.to[0] == check_cell_phone_number(to)
            assert sms.msg == truncate_sms(req_data['msg'])
            assert sms.signature == req_data['signature'][:len(sms.signature)]
