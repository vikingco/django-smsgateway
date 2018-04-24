# -*- coding: utf-8 -*-
from __future__ import absolute_import

from datetime import datetime
from requests import post
from time import mktime

from smsgateway.backends.base import SMSBackend


TREX_CALL = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://service-api.transatel.com/">
    <soapenv:Header/>
    <soapenv:Body>
        <ser:SendSMS>
            <ser:TransactionId>mig-{transaction_id}</ser:TransactionId>
            <ser:ClientLogin>{login}</ser:ClientLogin>
            <ser:ClientPwd>{password}</ser:ClientPwd>
            <ser:Profile></ser:Profile>
            <ser:AuditUserName></ser:AuditUserName>
            <ser:Msisdn>{msisdn}</ser:Mdisdn>
            <ser:ServiceName>MLM_BE_NOTIF_SMS</ser:ServiceName>
            <ser:MessageType>sms_txt_latin1</ser:MessageType>
            <ser:Message>{content}</ser:Message>
      </ser:SendSMS>
   </soapenv:Body>
</soapenv:Envelope>"""  # noqa


class TrexBackend(SMSBackend):
    def send(self, sms_request, account_dict):
        now = datetime.now()
        seconds = mktime(now.timetuple()) + now.microsecond / 1000000.0
        xml = TREX_CALL.format(transaction_id='{}-{}'.format(account_dict['transaction_prefix'], int(seconds * 1000)),
                               login=account_dict['username'],
                               password=account_dict['password'], msisdn=sms_request.to[0],
                               content=sms_request.msg.encode('latin-1'))

        try:
            post(account_dict['url'], data=xml,
                 headers={'Content-Type': 'text/xml; charset=utf-8', 'Content-Length': str(len(xml))},
                 timeout=5)
        except:
            return False

        return True

    def get_slug(self):
        return 'trex'
