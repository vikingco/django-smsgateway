# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='QueuedSMS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('to', models.CharField(max_length=32, verbose_name='receiver')),
                ('signature', models.CharField(max_length=32, verbose_name='signature')),
                ('content', models.TextField(help_text='SMS content', verbose_name='content')),
                ('created', models.DateTimeField(default=datetime.datetime.now)),
                ('using', models.CharField(help_text='Via which provider the SMS will be sent.', max_length=100, verbose_name='gateway', blank=True)),
                ('priority', models.CharField(default=b'2', max_length=1, choices=[(b'1', b'high'), (b'2', b'medium'), (b'3', b'low'), (b'9', b'deferred')])),
                ('reliable', models.BooleanField(default=False, verbose_name='is reliable')),
            ],
            options={
                'ordering': ('priority', 'created'),
                'get_latest_by': 'created',
                'verbose_name': 'Queued SMS',
                'verbose_name_plural': 'Queued SMSes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SMS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sent', models.DateTimeField(default=datetime.datetime.now, verbose_name='sent')),
                ('content', models.TextField(help_text='SMS content', verbose_name='content')),
                ('sender', models.CharField(max_length=32, verbose_name='sender', db_index=True)),
                ('to', models.CharField(max_length=32, verbose_name='receiver', db_index=True)),
                ('operator', models.IntegerField(default=0, verbose_name='Originating operator', choices=[(0, 'Unknown'), (1, 'Proximus'), (2, 'Mobistar'), (3, 'Base'), (999, 'Other')])),
                ('gateway', models.IntegerField(default=0, help_text='By which provider the SMS was handled.', verbose_name='gateway', choices=[(1, 'MobileWeb'), (3, 'SmsExtraPro'), (4, 'Spryng')])),
                ('backend', models.CharField(default=b'unknown', max_length=32, verbose_name='backend', db_index=True)),
                ('gateway_ref', models.CharField(help_text='A reference id for the gateway', max_length=32, verbose_name='gateway reference', blank=True)),
                ('direction', models.IntegerField(default=1, verbose_name='direction', choices=[(2, 'Both'), (1, 'Inbound'), (0, 'Outbound')])),
            ],
            options={
                'ordering': ('sent',),
                'get_latest_by': 'sent',
                'verbose_name': 'SMS',
                'verbose_name_plural': 'SMSes',
            },
            bases=(models.Model,),
        ),
    ]
