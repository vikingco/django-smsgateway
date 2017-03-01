# -*- encoding: utf-8 -*-

from datetime import datetime
from hashlib import md5
from logging import getLogger
from redis import ConnectionPool, Redis

from smsgateway.enums import DIRECTION_OUTBOUND
from smsgateway.models import SMS
from smsgateway.backends.base import SMSBackend
from smsgateway.sms import SMSRequest


logger = getLogger(__name__)


class RedistoreBackend(SMSBackend):

    def __init__(self):
        self.redis_key_prefix = None
        self.redis_pool = None
        self.redis_conn = None
        self.reference = None
        self.sender = None
        self.sms_data_iter = None
        self.sent_smses = []

    def prefix(self, key):
        return '{}{}'.format(self.redis_key_prefix, key)

    def _initialize(self, sms_request, account_dict):
        sms_list = self._get_sms_list(sms_request)
        if not len(sms_list):
            logger.error('Nothing to send. sms_request: {}'.format(sms_request))
            return False

        if sms_request.signature:
            self.sender = sms_request.signature
        else:
            self.sender = u'[{}]'.format(self.get_slug())

        self.sms_data_iter = SMSDataIterator(sms_list, account_dict)
        self.redis_key_prefix = account_dict['key_prefix']
        self.redis_pool = ConnectionPool(host=account_dict['host'],
                                         port=account_dict['port'],
                                         db=account_dict['dbn'],
                                         password=account_dict['pwd'])
        return True

    def _get_sms_list(self, sms_request):
        if not sms_request:
            return []
        sms_list = []
        self.reference = (datetime.now().strftime('%Y%m%d%H%M%S') + '+' + u''.join(sms_request.to[:1]))
        for msisdn in sms_request.to:
            sms_list.append(SMSRequest(msisdn,
                                       sms_request.msg,
                                       sms_request.signature,
                                       reliable=sms_request.reliable,
                                       reference=self.reference))
        return sms_list

    def _send_smses(self):
        if not self.sms_data_iter:
            return []

        pipe = self.redis_conn.pipeline(transaction=False)
        key = md5(self.reference).hexdigest()
        queue_key = self.prefix('smsreq:{}'.format(key))
        allqueues_key = self.prefix('outq')

        # feed the pipe
        for idx, sms_data in enumerate(self.sms_data_iter):
            source_sms = sms_data.pop('source_sms')
            sms_key = self.prefix('sms:{}:{}'.format((key, idx)))
            pipe.hmset(sms_key, sms_data)
            pipe.rpush(queue_key, sms_key)
            sent_sms = {
                'sender': self.sender,
                'to': sms_data['destination_addr'],
                'content': source_sms.msg,
                'backend': self.get_slug(),
                'direction': DIRECTION_OUTBOUND,
                'gateway_ref': source_sms.reference
            }
            self.sent_smses.append(sent_sms)
        pipe.lpush(allqueues_key, queue_key)

        # execute the pipe
        pipe_results = pipe.execute()
        return pipe_results

    def _check_sent_smses(self, results):
        """Check pipe execution results and create SMS objects."""
        if len(results) % 2 != 1:
            return False
        counter = 0
        while True:
            if len(results) == 1:
                break
            counter += 1
            created, listlen = results[:2]
            results = results[2:]
            instance_data = self.sent_smses.pop(0)
            if created and listlen == counter:
                SMS.objects.create(**instance_data)
        if results.pop():
            return True
        else:
            return False

    def send(self, sms_request, account_dict):
        """RedistoreBackend Entry Point"""
        self._initialize(sms_request, account_dict)
        self.redis_conn = Redis(connection_pool=self.redis_pool)
        redis_results = self._send_smses()
        check_result = self._check_sent_smses(redis_results)
        return check_result

    def get_slug(self):
        return 'redistore'


class SMSDataIterator:
    def __init__(self, sms_list, account_dict):
        self.sms_list = sms_list
        self.source_addr_ton = account_dict['source_addr_ton']
        self.source_addr = account_dict['source_addr']
        self.dest_addr_ton = account_dict['dest_addr_ton']

    def __iter__(self):
        return self

    def next(self):
        while len(self.sms_list):
            sms = self.sms_list.pop(0)
            text = sms.msg
            text = text.replace(u'€', u'EUR')
            text = text.encode('iso-8859-1', 'replace')

            return {
                'source_addr_ton': self.source_addr_ton,
                'source_addr': self.source_addr,
                'dest_addr_ton': self.dest_addr_ton,
                'destination_addr': sms.to[0],
                'short_message': text,
                'esme_vrfy_seqn': -1,
                'source_sms': sms
             }
        raise StopIteration
