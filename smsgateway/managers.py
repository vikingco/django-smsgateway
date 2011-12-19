from django.db import models

from smsgateway.enums import PRIORITY_MEDIUM, PRIORITY_DEFERRED

class QueuedSMSManager(models.Manager):
    def retry_deferred(self):
        return self.filter(priority=PRIORITY_DEFERRED).update(priority=PRIORITY_MEDIUM)
