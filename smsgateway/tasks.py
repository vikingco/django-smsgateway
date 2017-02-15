from datetime import datetime
from logging import getLogger
from redis import ConnectionPool, Redis

from django.conf import settings
from celery import shared_task as task
from django_statsd.clients import statsd

from lockfile import FileLock, AlreadyLocked, LockTimeout

from smsgateway import get_account, send, send_queued
from smsgateway.backends.base import SMSBackend
from smsgateway.enums import PRIORITY_DEFERRED
from smsgateway.models import SMS, QueuedSMS


logger = getLogger(__name__)

LOCK_WAIT_TIMEOUT = getattr(settings, "SMSES_LOCK_WAIT_TIMEOUT", -1)


@task
def send_smses(send_deferred=False, backend=None, limit=None):
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

        if isinstance(limit, int):
            to_send = to_send[:limit]

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


inq_ts_fmt = '%Y-%m-%d %H:%M:%S'


@task
def process_smses(smsk, sms_id, account_slug):
    smsobj = SMS.objects.get(pk=sms_id)
    smsbackend = SMSBackend()
    racc = get_account(account_slug)

    response = smsbackend.process_incoming(None, smsobj)
    if response is not None:
        signature = racc['reply_signature']
        # If an SMS account can receive but not send SMSes,
        # it can specify a preferred reply account
        reply_account = racc.get('reply_account', account_slug)
        success = send([smsobj.sender], response, signature, reply_account)
        if not success:
            send_queued(smsobj.sender, response, signature, reply_account)
    logger.debug("End processing incoming SMS key: %s", smsk)


def recv_smses(account_slug='redistore', async=False):
    def _(key):
        return '%s%s' % (racc['key_prefix'], key)

    count = 0
    racc = get_account(account_slug)
    rpool = ConnectionPool(host=racc['host'],
                           port=racc['port'],
                           db=racc['dbn'],
                           password=racc['pwd'])
    rconn = Redis(connection_pool=rpool)
    logger.info("Processing incoming SMSes for %s", account_slug)

    process_func = process_smses.delay if async else process_smses

    while True:
        smsk = rconn.lpop(_('inq'))
        if smsk is None:
            break
        count += 1
        logger.debug("Saving incoming SMS key: %s", smsk)
        smsd = rconn.hgetall(smsk)
        if not smsd:
            logger.error("SMS key %r is empty", smsk)
            continue
        # since microsecond are not always present - we remove them
        smsd['sent'] = datetime.strptime(smsd['sent'].split('.')[0],
                                         inq_ts_fmt)
        smsd['backend'] = account_slug
        # Compatibility with older code that expects numbers to starts with '+'
        msisdn_prefix = getattr(settings, 'SMSGATEWAY_MSISDN_PREFIX', '')
        if msisdn_prefix and not smsd['sender'].startswith(msisdn_prefix):
            smsd['sender'] = msisdn_prefix + smsd['sender']
        smsobj = SMS(**smsd)
        smsobj.save()
        process_func(smsk, smsobj.pk, account_slug)

    logger.info("End sharing out incoming SMSes for %s (%d saved).",
                account_slug, count)
