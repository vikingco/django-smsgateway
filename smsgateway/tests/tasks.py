import datetime
import hashlib
import redis

from django.conf import settings
from django.core import urlresolvers
from django.test import TestCase as DjangoTestCase

from smsgateway import enums
from smsgateway.models import SMS
from smsgateway.tasks import recv_smses
from smsgateway.backends.base import SMSBackend

from mock import call, patch


ACCOUNTS = getattr(settings, "SMSGATEWAY_ACCOUNTS", {})

def _(key):
    return '%s%s' % (ACCOUNTS['redistore']['key_prefix'], key)

def setup_redis_inq(rdb, count, **kwargs):
    source_addr = kwargs.get('source_addr', '+324832077%02d')
    destination_addr = kwargs.get('destination_addr', '15184')
    short_message = kwargs.get('short_message', 'Testing message %d')

    for i in xrange(count):
        sent_ts = datetime.datetime.now()
        sender = source_addr % i
        message_md5 = hashlib.md5('%d:%s:%s' % (
                sent_ts.toordinal(), sender, destination_addr))
        sms_data = {
            'sent': "%s" % sent_ts,
            'content': short_message % i,
            'sender': sender,
            'to': destination_addr,
            'operator': enums.OPERATOR_UNKNOWN,
            'gateway_ref': message_md5.hexdigest(),
            'backend': 'redistore'
        }
        smsk = "sms:%s" % message_md5.hexdigest()
        rdb.hmset(_(smsk), sms_data)
        rdb.rpush(_('inq'), _(smsk))


class RecvSMSesTestCase(DjangoTestCase):
    def setUp(self):
        self.conf = ACCOUNTS['redistore']
        self.rdb = redis.Redis(host=self.conf['host'], 
                               port=self.conf['port'],
                               db=self.conf['dbn'])
        self.assert_(SMS.objects.count() == 0)

    def tearDown(self):
        for key in self.rdb.keys('%s*' % self.conf['key_prefix']):
            self.rdb.delete(key)
        self.assert_(len(self.rdb.keys('%s*' % self.conf['key_prefix'])) == 0)
        SMS.objects.all().delete()

    def test_recv_smses(self):
        setup_redis_inq(self.rdb, 3)
        recv_smses()
        self.assert_(SMS.objects.count() == 3)

    def test_recv_smses_and_responses(self):
        def side_effect(_, sms):
            sms.save()
            return 'Successful!'

        setup_redis_inq(self.rdb, 3, short_message='SIM TOPUP %d')
        self.assert_(self.rdb.llen(_('inq')) == 3)

        with patch.object(SMSBackend, 'process_incoming') as mockf: 
            mockf.side_effect = side_effect
            recv_smses()

        mockf.assert_has_calls([call(None, SMS.objects.get(pk=1)),
                                call(None, SMS.objects.get(pk=3)),
                                call(None, SMS.objects.get(pk=5))])

        self.assert_(self.rdb.llen(_('outq')) == 3)
        self.assert_(self.rdb.llen(_('inq')) == 0)

        # 3 incoming SMSes + 3 outgoing TOPUP confirmation SMSes
        self.assert_(SMS.objects.count() == 6)
