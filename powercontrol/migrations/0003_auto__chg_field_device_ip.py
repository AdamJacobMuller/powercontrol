# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Device.ip'
        db.alter_column('powercontrol_device', 'ip', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255))

    def backwards(self, orm):

        # Changing field 'Device.ip'
        db.alter_column('powercontrol_device', 'ip', self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39, unique=True))

    models = {
        'powercontrol.device': {
            'Meta': {'object_name': 'Device'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'powercontrol.port': {
            'Meta': {'object_name': 'Port'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['powercontrol.Device']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'state': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True'})
        },
        'powercontrol.set': {
            'Meta': {'object_name': 'Set'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ports': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['powercontrol.Port']", 'symmetrical': 'False'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['powercontrol']