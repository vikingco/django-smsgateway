from django.db import models
from django.utils.translation import ugettext_lazy as _

from smsgateway.managers import QueuedSMSManager
from smsgateway.enums import PRIORITIES, PRIORITY_MEDIUM, PRIORITY_DEFERRED

import datetime

OPERATOR_UNKNOWN = 0
OPERATOR_PROXIMUS = 1
OPERATOR_MOBISTAR = 2
OPERATOR_BASE = 3
OPERATOR_OTHER = 999
OPERATOR_CHOICES = (
    (OPERATOR_UNKNOWN, _(u'Unknown')),
    (OPERATOR_PROXIMUS, u'Proximus'),
    (OPERATOR_MOBISTAR, u'Mobistar'),
    (OPERATOR_BASE, u'Base'),
    (OPERATOR_OTHER, _(u'Other')),
)

GATEWAY_MOBILEWEB = 1
GATEWAY_ZONG = 2
GATEWAY_SMSEXTRAPRO = 3
GATEWAY_SPRYNG = 4
GATEWAY_CHOICES = (
    (GATEWAY_MOBILEWEB, u'MobileWeb'),
    (GATEWAY_ZONG, u'Zong'),
    (GATEWAY_SMSEXTRAPRO, u'SmsExtraPro'),
    (GATEWAY_SPRYNG, u'Spryng'),
)

DIRECTION_BOTH = 2
DIRECTION_INBOUND = 1
DIRECTION_OUTBOUND = 0
DIRECTION_CHOICES = (
    (DIRECTION_BOTH, _(u'Both')),
    (DIRECTION_INBOUND, _(u'Inbound')),
    (DIRECTION_OUTBOUND, _(u'Outbound')),
)

class SMS(models.Model):
    sent = models.DateTimeField(default=datetime.datetime.now, verbose_name=_(u'sent'))
    content = models.TextField(verbose_name=_(u'content'), help_text=_(u'SMS content'))
    sender = models.CharField(max_length=32, verbose_name=_(u'sender'))
    to = models.CharField(max_length=32, verbose_name=_(u'receiver'))
    operator = models.IntegerField(choices=OPERATOR_CHOICES, default=OPERATOR_UNKNOWN, verbose_name=_(u'Originating operator'))
    gateway = models.IntegerField(choices=GATEWAY_CHOICES, default=0, verbose_name=_(u'gateway'), help_text=_(u'By which provider the SMS was handled.'))
    backend = models.CharField(max_length=32, db_index=True, default='unknown', verbose_name=_(u'backend'))
    gateway_ref = models.CharField(max_length=32, blank=True, verbose_name=_(u'gateway reference'), help_text=_(u'A reference id for the gateway'))
    direction = models.IntegerField(choices=DIRECTION_CHOICES, default=DIRECTION_INBOUND, verbose_name=_(u'direction'))

    class Meta:
        get_latest_by = 'sent'
        ordering = ('sent',)
        verbose_name = _(u'SMS')
        verbose_name_plural = _(u'SMSes')

    def __unicode__(self):
        return u'SMS: "%s" from "%s"' % (self.content, self.sender)


class QueuedSMS(models.Model):
    to = models.CharField(max_length=32, verbose_name=_(u'receiver'))
    signature = models.CharField(max_length=32, verbose_name=_(u'signature'))
    content = models.TextField(verbose_name=_(u'content'), help_text=_(u'SMS content'))
    created = models.DateTimeField(default=datetime.datetime.now)
    using = models.CharField(blank=True, max_length=100,
                             verbose_name=_(u'gateway'),
                             help_text=_(u'Via which provider the SMS will be sent.'))
    priority = models.CharField(max_length=1, choices=PRIORITIES, default=PRIORITY_MEDIUM)
    reliable = models.BooleanField(default=False, blank=True, verbose_name=_(u'is reliable'))

    objects = QueuedSMSManager()

    class Meta:
        get_latest_by = 'created'
        ordering = ('priority', 'created',)
        verbose_name = _(u'Queued SMS')
        verbose_name_plural = _(u'Queued SMSes')

    def defer(self):
        self.priority = PRIORITY_DEFERRED
        self.save()
