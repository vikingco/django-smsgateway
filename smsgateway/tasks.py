import datetime
import logging
import redis

from django.conf import settings
from celery.decorators import task

from lockfile import FileLock, AlreadyLocked, LockTimeout

from smsgateway import get_account, send, send_queued
from smsgateway.backends.base import SMSBackend
from smsgateway.enums import PRIORITY_DEFERRED
from smsgateway.models import SMS, QueuedSMS


logger = logging.getLogger(__name__)

LOCK_WAIT_TIMEOUT = getattr(settings, "SMSES_LOCK_WAIT_TIMEOUT", -1)
ACCOUNTS = getattr(settings, "SMSGATEWAY_ACCOUNTS", {})

@task
def send_smses(send_deferred=False, backend=None):
    # Get lock so there is only one sms sender at the same time.
    if send_deferred:
        lock = FileLock('send_sms_deferred')
    else:
        lock = FileLock('send_sms')
    try:
        lock.acquire(LOCK_WAIT_TIMEOUT)
    except AlreadyLocked:
        logger.info('Could not acquire lock.')
        return
    except LockTimeout:
        logger.info('Lock timed out.')
        return

    try:
        # Get SMSes that need to be sent (deferred or non-deferred)
        if send_deferred:
            to_send = QueuedSMS.objects.filter(priority=PRIORITY_DEFERRED)
        else:
            to_send = QueuedSMS.objects.exclude(priority=PRIORITY_DEFERRED)

        logger.info("Trying to send %i messages." % to_send.count())

        # Send each SMS
        for sms in to_send:
            if backend:
                sms_using = backend
            else:
                sms_using = None if sms.using == '__none__' else sms.using
            if send(sms.to, sms.content, sms.signature, sms_using, sms.reliable):
                # Successfully sent, remove from queue
                logger.info("SMS to %s sent." % sms.to)
                sms.delete()
            else:
                # Failed to send, defer SMS
                logger.info("SMS to %s failed." % sms.to)
                sms.defer()
    finally:
        lock.release()


inq_ts_fmt = '%Y-%m-%d %H:%M:%S.%f'

@task
def recv_smses():
    def _(key):
        return '%s%s' % (racc['key_prefix'], key)

    count = 0
    racc = ACCOUNTS['redistore']
    rpool = redis.ConnectionPool(host=racc['host'], 
                                 port=racc['port'], 
                                 db=racc['dbn'])
    rconn = redis.Redis(connection_pool=rpool)
    smsbackend = SMSBackend()
    logger.info("Processing incoming SMSes")

    while True:
        smsk = rconn.rpoplpush(_('inq'), _('mvne:inq'))
        if not rconn.llen(_('mvne:inq')):
            break
        count += 1
        logger.debug("Processing incoming SMS key: %s" % smsk)
        smsd = rconn.hgetall(smsk)
        smsd['sent'] = datetime.datetime.strptime(smsd['sent'], inq_ts_fmt)
        smsobj = SMS(**smsd)
        response = smsbackend.process_incoming(None, smsobj)
        if response is not None:
            signature = get_account('redistore')['reply_signature']
            success = send([smsobj.sender], response, signature, 'redistore')
            if not success:
                send_queued(smsobj.sender, response, signature, 'redistore')
        if rconn.lrem(_('mvne:inq'), smsk, 1) == 0:
            logger.error("SMS key %r doesn't exist in %r" 
                         % (smsk, _('mvne:inq')))
        if not rconn.delete(smsk):
            logger.error("SMS Hash %r doesn't exist" % smsk)
        logger.debug("End processing incoming SMS key: %s" % smsk)

    logger.info("End processing incoming SMSes (%d processed)" % count)
