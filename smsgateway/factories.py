# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from factory import DjangoModelFactory, Sequence
from smsgateway.models import SMS


class SMSFactory(DjangoModelFactory):
    class Meta:
        model = SMS

    content = 'This is a test'
    sender = Sequence(lambda n: u'+32476{0:06d}'.format(n))
    to = Sequence(lambda n: u'+32476{0:06d}'.format(n))
