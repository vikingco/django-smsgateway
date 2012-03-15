from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = 'Do one pass through the SMS queue, attempting to send all SMSes.'

    def handle_noargs(self, **options):
        from smsgateway.tasks import send_smses
        send_smses()
