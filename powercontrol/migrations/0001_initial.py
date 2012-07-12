# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Device'
        db.create_table('powercontrol_device', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ip', self.gf('django.db.models.fields.GenericIPAddressField')(unique=True, max_length=39)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('powercontrol', ['Device'])

        # Adding model 'Port'
        db.create_table('powercontrol_port', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['powercontrol.Device'])),
            ('port', self.gf('django.db.models.fields.IntegerField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True, null=True)),
            ('state', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('powercontrol', ['Port'])

        # Adding model 'Set'
        db.create_table('powercontrol_set', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('powercontrol', ['Set'])

        # Adding M2M table for field ports on 'Set'
        db.create_table('powercontrol_set_ports', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('set', models.ForeignKey(orm['powercontrol.set'], null=False)),
            ('port', models.ForeignKey(orm['powercontrol.port'], null=False))
        ))
        db.create_unique('powercontrol_set_ports', ['set_id', 'port_id'])


    def backwards(self, orm):
        # Deleting model 'Device'
        db.delete_table('powercontrol_device')

        # Deleting model 'Port'
        db.delete_table('powercontrol_port')

        # Deleting model 'Set'
        db.delete_table('powercontrol_set')

        # Removing M2M table for field ports on 'Set'
        db.delete_table('powercontrol_set_ports')


    models = {
        'powercontrol.device': {
            'Meta': {'object_name': 'Device'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.GenericIPAddressField', [], {'unique': 'True', 'max_length': '39'}),
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