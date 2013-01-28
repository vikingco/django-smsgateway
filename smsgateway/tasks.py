from django.conf import settings
from celery.decorators import task

from lockfile import FileLock, AlreadyLocked, LockTimeout

from smsgateway import send
from smsgateway.enums import PRIORITY_DEFERRED
from smsgateway.models import QueuedSMS

import logging

logger = logging.getLogger(__name__)

LOCK_WAIT_TIMEOUT = getattr(settings, "SMSES_LOCK_WAIT_TIMEOUT", -1)

@task
def send_smses(send_deferred=False):
    # Get lock so there is only one sms sender at the same time.
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
