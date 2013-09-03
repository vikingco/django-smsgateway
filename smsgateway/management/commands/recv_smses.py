from django.core.management.base import NoArgsCommand
from optparse import make_option
from smsgateway.tasks import recv_smses


class Command(NoArgsCommand):
    help = 'Receive SMSes from the Redis queue.'
    option_list = NoArgsCommand.option_list + (
            make_option('--backend',
                help='Slug of the SMS backend to read from'),
            )

    def handle_noargs(self, **options):
        recv_smses(options['backend'])
