from smsgateway.utils import check_cell_phone_number, truncate_sms


class SMSRequest(object):
    def __init__(self, to, msg, signature, reliable=False, reference=None):
        """
        The 'to' parameter is a list of mobile numbers including country prefix.
        The 'msg' parameter is a unicode object of 160 characters. Please keep in mind that the actual
        supported character set depends on the SMS gateway provider and phone model.
        The validity of the 'signature' depends on the SMS gateway provider you are using.

        >>> sms_request = SMSRequest(to='+32472123456;+3298723456', u'Hello, world!', signature='9898')
        """
        self.to = [check_cell_phone_number(n) for n in (to.split(';') if isinstance(to, basestring) else to)]
        self.msg = truncate_sms(msg)
        self.signature = signature[:16] if signature[1:].isdigit() else signature[:11]
        self.reliable = reliable
        self.reference = reference


class JasminSMSRequest(SMSRequest):
    def __init__(self, to, msg, signature, reliable=False, reference=None):
        """
        The Jasmin backend can handle longer messages so we send truncate_sms a bigger max_length here
        """

        super(JasminSMSRequest, self).__init__(to, '', signature, reliable, reference)
        self.msg = truncate_sms(msg, 500)
