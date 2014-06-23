import datetime
import logging
import redis

from django.conf import settings
from celery.task import task
from django_statsd.clients import statsd

from lockfile import FileLock, AlreadyLocked, LockTimeout

from smsgateway import get_account, send, send_queued
from smsgateway.backends.base import SMSBackend
from smsgateway.enums import PRIORITY_DEFERRED
from smsgateway.models import SMS, QueuedSMS


logger = logging.getLogger(__name__)

LOCK_WAIT_TIMEOUT = getattr(settings, "SMSES_LOCK_WAIT_TIMEOUT", -1)

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

    successes, failures = 0, 0
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
                successes += 1
            else:
                # Failed to send, defer SMS
                logger.info("SMS to %s failed." % sms.to)
                sms.defer()
                failures += 1
    finally:
        lock.release()
        if successes and failures:
            statsd.gauge('smsgateway.success_rate', successes / failures)
        else:
            statsd.gauge('smsgateway.success_rate', 1)


inq_ts_fmt = '%Y-%m-%d %H:%M:%S.%f'

@task
def recv_smses(account_slug='redistore'):
    def _(key):
        return '%s%s' % (racc['key_prefix'], key)

    count = 0
    racc = get_account(account_slug)
    rpool = redis.ConnectionPool(host=racc['host'],
                                 port=racc['port'],
                                 db=racc['dbn'])
    rconn = redis.Redis(connection_pool=rpool)
    smsbackend = SMSBackend()
    logger.info("Processing incoming SMSes for %s", account_slug)

    while True:
        smsk = rconn.rpoplpush(_('inq'), _('mvne:inq'))
        if not rconn.llen(_('mvne:inq')):
            break
        count += 1
        logger.debug("Processing incoming SMS key: %s", smsk)
        smsd = rconn.hgetall(smsk)
        if not smsd:
            logger.error("SMS key %r is empty", smsk)
            continue
        smsd['sent'] = datetime.datetime.strptime(smsd['sent'], inq_ts_fmt)
        smsd['backend'] = account_slug
        smsobj = SMS(**smsd)
        response = smsbackend.process_incoming(None, smsobj)
        if response is not None:
            signature = racc['reply_signature']
            success = send([smsobj.sender], response, signature, account_slug)
            if not success:
                send_queued(smsobj.sender, response, signature, account_slug)
        if rconn.lrem(_('mvne:inq'), smsk, 1) == 0:
            logger.error("SMS key %r doesn't exist in %r",
                         smsk, _('mvne:inq'))
        if not rconn.delete(smsk):
            logger.error("SMS Hash %r doesn't exist" % smsk)
        logger.debug("End processing incoming SMS key: %s", smsk)

    logger.info("End processing incoming SMSes for %s (%d processed)", account_slug, count)
