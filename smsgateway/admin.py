from django.contrib import admin

from smsgateway.models import SMS, QueuedSMS

class SMSAdmin(admin.ModelAdmin):
    date_hierarchy = 'sent'
    list_display = ('direction', 'sent', 'sender', 'to', 'content', 'operator', 'backend', 'gateway', 'gateway_ref',)
    search_fields = ('sender', 'to', 'content',)
    list_filter = ('operator', 'direction', 'gateway', 'backend')

admin.site.register(SMS, SMSAdmin)


class QueuedSMSAdmin(admin.ModelAdmin):
    list_display = ('to', 'signature', 'content', 'created')
    search_fields = ('to', 'signature', 'content')
    list_filter = ('signature', 'created')

admin.site.register(QueuedSMS, QueuedSMSAdmin)

