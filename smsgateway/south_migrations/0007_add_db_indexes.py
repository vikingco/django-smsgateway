# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'SMS', fields ['sender']
        db.create_index('smsgateway_sms', ['sender'])

        # Adding index on 'SMS', fields ['to']
        db.create_index('smsgateway_sms', ['to'])


    def backwards(self, orm):
        # Removing index on 'SMS', fields ['to']
        db.delete_index('smsgateway_sms', ['to'])

        # Removing index on 'SMS', fields ['sender']
        db.delete_index('smsgateway_sms', ['sender'])


    models = {
        'smsgateway.queuedsms': {
            'Meta': {'ordering': "('priority', 'created')", 'object_name': 'QueuedSMS'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.CharField', [], {'default': "'2'", 'max_length': '1'}),
            'reliable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'signature': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'to': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'using': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'smsgateway.sms': {
            'Meta': {'ordering': "('sent',)", 'object_name': 'SMS'},
            'backend': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '32', 'db_index': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'direction': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'gateway': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'gateway_ref': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'operator': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sender': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'to': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'})
        }
    }

    complete_apps = ['smsgateway']