from django.conf import settings
from celery.decorators import task

from lockfile import FileLock, AlreadyLocked, LockTimeout

from smsgateway import send
from smsgateway.models import QueuedSMS

import logging


# lock timeout value. how long to wait for the lock to become available.
# default behavior is to never wait for the lock to be available.
LOCK_WAIT_TIMEOUT = getattr(settings, "SMSES_LOCK_WAIT_TIMEOUT", -1)

@task
def send_smses():
    # Enable lock (only one sms sender at the same time)
    lock = FileLock("send_sms")

    logging.debug("acquiring lock...")
    try:
        lock.acquire(LOCK_WAIT_TIMEOUT)
    except AlreadyLocked:
        logging.debug("lock already in place. quitting.")
        return
    except LockTimeout:
        logging.debug("waiting for the lock timed out. quitting.")
        return
    logging.debug("acquired.")

    try:
        logging.info("%i sms messages to be send." % QueuedSMS.objects.count())

        for sms in list(QueuedSMS.objects.all()):
            sms_using = None if sms.using == '__none__' else sms.using
            if send(sms.to, sms.content, sms.signature, using=sms_using, reliable=sms.reliable):
                # On succes
                logging.info("SMS to %s sent." % sms.to)
                sms.delete()
            else:
                sms.defer()
                # Failure
                logging.info("SMS to %s failed." % sms.to)
    finally:
        lock.release()


@task
def send_deferred_smses(self):
    """
    Attempt to resend any deferred smses.
    """
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    count = QueuedSMS.objects.retry_deferred()
    logging.info("%s message(s) retried" % count)
