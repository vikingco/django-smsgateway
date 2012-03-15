from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = 'Attempt to resend any deferred smses.'

    def handle_noargs(self, **options):
        from smsgateway.tasks import send_deferred_smses
        send_deferred_smses()
