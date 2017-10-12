# encoding: utf-8
from __future__ import absolute_import
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'QueuedSMS.created'
        db.add_column('smsgateway_queuedsms', 'created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'QueuedSMS.created'
        db.delete_column('smsgateway_queuedsms', 'created')


    models = {
        'smsgateway.queuedsms': {
            'Meta': {'object_name': 'QueuedSMS'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'signature': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'to': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'smsgateway.sms': {
            'Meta': {'object_name': 'SMS'},
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
