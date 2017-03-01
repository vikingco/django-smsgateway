from django.db import models
from django.utils.translation import ugettext_lazy

from smsgateway.enums import (OPERATOR_CHOICES, OPERATOR_UNKNOWN, GATEWAY_CHOICES, DIRECTION_CHOICES, DIRECTION_INBOUND,
                              PRIORITIES, PRIORITY_MEDIUM, PRIORITY_DEFERRED)

from datetime import datetime


class SMS(models.Model):
    sent = models.DateTimeField(default=datetime.now, verbose_name=ugettext_lazy(u'sent'))
    content = models.TextField(verbose_name=ugettext_lazy(u'content'), help_text=ugettext_lazy(u'SMS content'))
    sender = models.CharField(max_length=32, verbose_name=ugettext_lazy(u'sender'), db_index=True)
    to = models.CharField(max_length=32, verbose_name=ugettext_lazy(u'receiver'), db_index=True)
    operator = models.IntegerField(choices=OPERATOR_CHOICES, default=OPERATOR_UNKNOWN,
                                   verbose_name=ugettext_lazy(u'Originating operator'))
    gateway = models.IntegerField(choices=GATEWAY_CHOICES, default=0, verbose_name=ugettext_lazy(u'gateway'),
                                  help_text=ugettext_lazy(u'By which provider the SMS was handled.'))
    backend = models.CharField(max_length=32, db_index=True, default='unknown', verbose_name=ugettext_lazy(u'backend'))
    gateway_ref = models.CharField(max_length=64, blank=True, verbose_name=ugettext_lazy(u'gateway reference'),
                                   help_text=ugettext_lazy(u'A reference id for the gateway'))
    direction = models.IntegerField(choices=DIRECTION_CHOICES, default=DIRECTION_INBOUND,
                                    verbose_name=ugettext_lazy(u'direction'))

    class Meta:
        get_latest_by = 'sent'
        ordering = ('sent',)
        verbose_name = ugettext_lazy(u'SMS')
        verbose_name_plural = ugettext_lazy(u'SMSes')

    def __unicode__(self):
        return u'SMS: "{}" from "{}"'.format(self.content, self.sender)


class QueuedSMS(models.Model):
    to = models.CharField(max_length=32, verbose_name=ugettext_lazy(u'receiver'))
    signature = models.CharField(max_length=32, verbose_name=ugettext_lazy(u'signature'))
    content = models.TextField(verbose_name=ugettext_lazy(u'content'), help_text=ugettext_lazy(u'SMS content'))
    created = models.DateTimeField(default=datetime.now)
    using = models.CharField(blank=True, max_length=100, verbose_name=ugettext_lazy(u'gateway'),
                             help_text=ugettext_lazy(u'Via which provider the SMS will be sent.'))
    priority = models.CharField(max_length=1, choices=PRIORITIES, default=PRIORITY_MEDIUM)
    reliable = models.BooleanField(default=False, blank=True, verbose_name=ugettext_lazy(u'is reliable'))

    class Meta:
        get_latest_by = 'created'
        ordering = ('priority', 'created',)
        verbose_name = ugettext_lazy(u'Queued SMS')
        verbose_name_plural = ugettext_lazy(u'Queued SMSes')

    def defer(self):
        self.priority = PRIORITY_DEFERRED
        self.save()
