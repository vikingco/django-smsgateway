# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smsgateway', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sms',
            name='gateway_ref',
            field=models.CharField(help_text='A reference id for the gateway', max_length=64, verbose_name='gateway reference', blank=True),
        ),
    ]
