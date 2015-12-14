# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import factory
from smsgateway.models import SMS


class SMSFactory(factory.DjangoModelFactory):
    FACTORY_FOR = SMS

    content = 'This is a test'
    sender = factory.Sequence(lambda n: u"+32476{0:06d}".format(n))
    to = factory.Sequence(lambda n: u"+32476{0:06d}".format(n))
