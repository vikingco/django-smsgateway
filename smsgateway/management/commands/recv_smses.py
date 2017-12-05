from __future__ import absolute_import
from django.core.management.base import BaseCommand
from smsgateway.tasks import recv_smses


class Command(BaseCommand):
    help = 'Receive SMSes from the Redis queue.'

    def add_arguments(self, parser):
            parser.add_argument('--backend', help='Slug of the SMS backend to read from'),
            parser.add_argument('--async',
                                action='store_true',
                                dest='async',
                                default=False,
                                help='Process the SMSes via asynchronously via Celery')

    def handle(self, *args, **options):
        recv_smses(options['backend'], options['async'])
