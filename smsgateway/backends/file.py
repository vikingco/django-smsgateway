import codecs

from django.http import HttpResponse

from smsgateway.backends.base import SMSBackend


class FileBackend(SMSBackend):
    """
    Backend for debugging purposes. Writes all SMSes to a file.
    """
    def get_send_url(self, sms_request, account_dict):
        path = account_dict['path']

        f = codecs.open(path, 'ab', 'utf8')
        f.write(u'%s,%s,%s\n' % (sms_request.to[0], sms_request.msg, sms_request.signature))
        f.close()

        return None

    def validate_send_result(self, result):
        return True

    def handle_incoming(self, request, reply_using=None):
        return HttpResponse('')

    def get_slug(self):
        return 'file'

    def get_url_capacity(self):
        return 1
