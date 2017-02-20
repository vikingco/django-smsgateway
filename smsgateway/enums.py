from django.utils.translation import ugettext_lazy

OPERATOR_UNKNOWN = 0
OPERATOR_PROXIMUS = 1
OPERATOR_MOBISTAR = 2
OPERATOR_BASE = 3
OPERATOR_OTHER = 999
OPERATOR_CHOICES = (
    (OPERATOR_UNKNOWN, ugettext_lazy(u'Unknown')),
    (OPERATOR_PROXIMUS, u'Proximus'),
    (OPERATOR_MOBISTAR, u'Mobistar'),
    (OPERATOR_BASE, u'Base'),
    (OPERATOR_OTHER, ugettext_lazy(u'Other')),
)

GATEWAY_MOBILEWEB = 1
GATEWAY_SMSEXTRAPRO = 3
GATEWAY_SPRYNG = 4
GATEWAY_CHOICES = (
    (GATEWAY_MOBILEWEB, u'MobileWeb'),
    (GATEWAY_SMSEXTRAPRO, u'SmsExtraPro'),
    (GATEWAY_SPRYNG, u'Spryng'),
)

DIRECTION_BOTH = 2
DIRECTION_INBOUND = 1
DIRECTION_OUTBOUND = 0
DIRECTION_CHOICES = (
    (DIRECTION_BOTH, ugettext_lazy(u'Both')),
    (DIRECTION_INBOUND, ugettext_lazy(u'Inbound')),
    (DIRECTION_OUTBOUND, ugettext_lazy(u'Outbound')),
)

PRIORITY_HIGH = '1'
PRIORITY_MEDIUM = '2'
PRIORITY_LOW = '3'
PRIORITY_DEFERRED = '9'

PRIORITIES = (
    (PRIORITY_HIGH,     'high'),
    (PRIORITY_MEDIUM,   'medium'),
    (PRIORITY_LOW,      'low'),
    (PRIORITY_DEFERRED, 'deferred'),
)
