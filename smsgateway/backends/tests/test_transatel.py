from __future__ import unicode_literals

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from pytest import fixture, mark, raises
from requests import exceptions
import responses  # noqa: T005

from smsgateway.models import SMS
from smsgateway.sms import SMSRequest
from ..transatel import TransatelBackend


@fixture
def sms_request():
    return SMSRequest(['+32474123456'], 'hello world', '1820')


@fixture
def account_dict():
    return {
        'username': 'sonic',
        'password': 'the hedgehog',
        'servicename': 'transatel',
        'url': 'http://transatel'
    }


@fixture
def invalid_response_body():
    return b'<xml><body>bogus</body></xml>'


@fixture
def valid_response_body():
    return b'<?xml version=\'1.0\' encoding=\'UTF-8\'?><S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body><ns2:SwitchCosResponse xmlns:ns2="http://service-api.transatel.com/"><ns2:SwitchCosResult><ns2:result>0</ns2:result><ns2:errorReason>OK</ns2:errorReason><ns2:transactionId>mig-4</ns2:transactionId></ns2:SwitchCosResult></ns2:SwitchCosResponse></S:Body></S:Envelope>'  # noqa


def test_init_set_default_template():
    backend = TransatelBackend()
    assert backend.template == TransatelBackend.TEMPLATE


def test_init_set_own_template():
    backend = TransatelBackend(template='<my backend/>')
    assert backend.template == '<my backend/>'


def test_get_send_url(sms_request, account_dict):
    backend = TransatelBackend()
    assert backend.get_send_url(sms_request, account_dict) == account_dict['url']


@mark.django_db
def test_send_calls_transatel_soap_url(sms_request, account_dict):
    backend = TransatelBackend()
    with patch('smsgateway.backends.transatel.post') as mock_post:
        backend.send(sms_request, account_dict)
        assert mock_post.called


@mark.django_db
def test_send_calls_transatel_xml(sms_request, account_dict):
    backend = TransatelBackend()
    with patch('smsgateway.backends.transatel.post') as mock_post:
        backend.send(sms_request, account_dict)
        kwargs = mock_post.call_args[1]
        assert account_dict['username'] in kwargs['data']
        assert account_dict['password'] in kwargs['data']
        assert sms_request.msg in kwargs['data']


def test_send_no_url_does_not_send(sms_request, account_dict):
    account_dict['url'] = None
    backend = TransatelBackend()
    with patch('smsgateway.backends.transatel.post') as mock_post:
        assert not backend.send(sms_request, account_dict)
        assert not mock_post.called


def test_send_connection_error_does_not_send(sms_request, account_dict):
    backend = TransatelBackend()
    with patch('smsgateway.backends.transatel.post', side_effect=exceptions.ConnectionError):
        assert not backend.send(sms_request, account_dict)


def test_send_timeout_error_does_not_send(sms_request, account_dict):
    backend = TransatelBackend()
    with patch('smsgateway.backends.transatel.post', side_effect=exceptions.Timeout):
        assert not backend.send(sms_request, account_dict)


def test_send_any_exception_does_not_send(sms_request, account_dict):
    backend = TransatelBackend()
    with patch('smsgateway.backends.transatel.post', side_effect=ValueError):
        assert not backend.send(sms_request, account_dict)


@responses.activate
def test_send_wrong_status_code_does_not_send(sms_request, account_dict):
    backend = TransatelBackend()
    responses.add(responses.POST, account_dict['url'], '', status=400)
    assert not backend.send(sms_request, account_dict)


@mark.django_db
@responses.activate
def test_send_invalid_result_does_not_create_sms(sms_request, account_dict, invalid_response_body):
    backend = TransatelBackend()
    responses.add(responses.POST, account_dict['url'], invalid_response_body)
    backend.send(sms_request, account_dict)
    assert not SMS.objects.exists()


@mark.django_db
@responses.activate
def test_send_creates_sms(sms_request, account_dict, valid_response_body):
    backend = TransatelBackend()
    responses.add(responses.POST, account_dict['url'], valid_response_body)
    backend.send(sms_request, account_dict)
    assert SMS.objects.exists()


@mark.django_db
def test_send_calls_transatel_headers(sms_request, account_dict):
    backend = TransatelBackend()
    with patch('smsgateway.backends.transatel.post') as mock_post:
        backend.send(sms_request, account_dict)
        kwargs = mock_post.call_args[1]
        assert kwargs['headers']['Content-Type'] == 'text/xml; charset=utf-8'
        assert kwargs['headers']['Content-Length'] == str(len(kwargs['data']))


def test_get_slug_is_transatel():
    backend = TransatelBackend()
    assert backend.get_slug() == 'transatel'


def test_validate_send_result_passing(valid_response_body):
    backend = TransatelBackend()
    assert backend.validate_send_result(valid_response_body)


def test_validate_send_result_invalid(invalid_response_body):
    backend = TransatelBackend()
    assert not backend.validate_send_result(invalid_response_body)


def test_check_incoming_not_supported_yet(rf):
    backend = TransatelBackend()
    with raises(NotImplementedError):
        backend.handle_incoming(rf.get('/'))


def test_get_url_capacity():
    backend = TransatelBackend()
    assert backend.get_url_capacity() == 1


def test_get_gateway_ref_passing(valid_response_body):
    backend = TransatelBackend()
    assert backend.get_gateway_ref('somref', valid_response_body) == 'mig-4'


def test_get_gateway_ref_invalid(invalid_response_body):
    backend = TransatelBackend()
    assert backend.get_gateway_ref('somref', invalid_response_body) == 'somref'
