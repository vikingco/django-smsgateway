from lockfile import FileLock, AlreadyLocked, LockTimeout
import logging

from django.conf import settings
from django.core.management.base import NoArgsCommand

from smsgateway.models import QueuedSMS
from smsgateway import send

# lock timeout value. how long to wait for the lock to become available.
# default behavior is to never wait for the lock to be available.
LOCK_WAIT_TIMEOUT = getattr(settings, "SMSES_LOCK_WAIT_TIMEOUT", -1)

class Command(NoArgsCommand):
    help = 'Do one pass through the SMS queue, attempting to send all SMSes.'

    def handle_noargs(self, **options):
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
