from __future__ import absolute_import
from logging import getLogger

from django.conf import settings
from django.core.management.base import BaseCommand

from smsgateway.tasks import _send_smses as send_smses

LOCK_WAIT_TIMEOUT = getattr(settings, 'SMSES_LOCK_WAIT_TIMEOUT', -1)

logger = getLogger(__name__)


class Command(BaseCommand):
    help = 'Send SMSes in the queue. Defer the failed ones. Pass --send-deferred to retry those.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--send-deferred',
            dest='send_deferred',
            action='store_true',
            help='Whether to send the deferred smses. Default is all non-deferred.'
        ),
        parser.add_argument(
            '--backend',
            dest='backend',
            action='store',
            help='Whether to use a certain backend.'
        ),
        parser.add_argument(
            '--limit',
            dest='limit',
            action='store',
            help='Limit the number of smses. Default is unlimited.'
        ),

    def handle(self, *args, **options):
        send_smses(options['send_deferred'], options['backend'], options['limit'])
