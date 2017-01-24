from django.test import TestCase


from smsgateway.utils import check_cell_phone_number


class CheckNumberTest(TestCase):
    def test_international_format(self):
        return check_cell_phone_number('+32478123456') == '+32478123456'

    def test_international_format_without_plus(self):
        return check_cell_phone_number('32478123456') == '+32478123456'

    def test_national_format(self):
        return check_cell_phone_number('0478123456') == '+32478123456'

    def test_national_format_without_leading_zero(self):
        return check_cell_phone_number('478123456') == '+32478123456'
