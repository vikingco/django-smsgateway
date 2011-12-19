import logging
from django.core.management.base import NoArgsCommand
from smsgateway.models import QueuedSMS

class Command(NoArgsCommand):
    help = 'Attempt to resend any deferred mail.'

    def handle_noargs(self, **options):
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
        count = QueuedSMS.objects.retry_deferred()
        logging.info("%s message(s) retried" % count)
