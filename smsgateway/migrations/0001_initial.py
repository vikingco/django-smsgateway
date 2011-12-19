
from south.db import db
from django.db import models
from smsgateway.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'SMS'
        db.create_table('smsgateway_sms', (
            ('id', orm['smsgateway.SMS:id']),
            ('sent', orm['smsgateway.SMS:sent']),
            ('content', orm['smsgateway.SMS:content']),
            ('sender', orm['smsgateway.SMS:sender']),
            ('to', orm['smsgateway.SMS:to']),
            ('operator', orm['smsgateway.SMS:operator']),
            ('gateway', orm['smsgateway.SMS:gateway']),
            ('backend', orm['smsgateway.SMS:backend']),
            ('gateway_ref', orm['smsgateway.SMS:gateway_ref']),
            ('direction', orm['smsgateway.SMS:direction']),
        ))
        db.send_create_signal('smsgateway', ['SMS'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'SMS'
        db.delete_table('smsgateway_sms')
        
    
    
    models = {
        'smsgateway.sms': {
            'backend': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '32', 'db_index': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'direction': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'gateway': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'gateway_ref': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'operator': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sender': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'to': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }
    
    complete_apps = ['smsgateway']
