from __future__ import absolute_import

from mock import patch
from django.test import TestCase

from smsgateway.utils import check_cell_phone_number, is_pre_django2


class CheckNumberTest(TestCase):
    def test_international_format(self):
        return check_cell_phone_number('+32478123456') == '32478123456'

    def test_international_format_without_plus(self):
        return check_cell_phone_number('32478123456') == '32478123456'

    def test_national_format(self):
        return check_cell_phone_number('0478123456') == '32478123456'

    def test_national_format_without_leading_zero(self):
        return check_cell_phone_number('478123456') == '32478123456'


class CheckPreDjango2(TestCase):
    def test_check_pre2(self):
        with patch('smsgateway.utils.django_version', return_value='1.11'):
            assert is_pre_django2()

    def test_check_post2(self):
        with patch('smsgateway.utils.django_version', return_value='2.0.2'):
            assert not is_pre_django2()
