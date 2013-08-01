from django.core.management.base import NoArgsCommand
from smsgateway.tasks import recv_smses


class Command(NoArgsCommand):
    help = 'Receive SMSes from the Redis queue.'

    def handle_noargs(self, **options):
        recv_smses()
