# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ResourceSetting'
        db.create_table(u'resource_mgr_resourcesetting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('unit', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('conversion_rate', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('winning_order', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'resource_mgr', ['ResourceSetting'])

        # Adding unique constraint on 'ResourceSetting', fields ['name']
        db.create_unique(u'resource_mgr_resourcesetting', ['name'])

        # Adding model 'ResourceBlackoutDate'
        db.create_table(u'resource_mgr_resourceblackoutdate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
        ))
        db.send_create_signal(u'resource_mgr', ['ResourceBlackoutDate'])

        # Adding model 'EnergyUsage'
        db.create_table(u'resource_mgr_energyusage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['team_mgr.Team'])),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 11, 21, 0, 0))),
            ('time', self.gf('django.db.models.fields.TimeField')(default=datetime.time(23, 19, 22, 836630))),
            ('manual_meter_reading', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('usage', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'resource_mgr', ['EnergyUsage'])

        # Adding unique constraint on 'EnergyUsage', fields ['date', 'team']
        db.create_unique(u'resource_mgr_energyusage', ['date', 'team_id'])

        # Adding model 'WaterUsage'
        db.create_table(u'resource_mgr_waterusage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['team_mgr.Team'])),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 11, 21, 0, 0))),
            ('time', self.gf('django.db.models.fields.TimeField')(default=datetime.time(23, 19, 22, 836630))),
            ('manual_meter_reading', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('usage', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'resource_mgr', ['WaterUsage'])

        # Adding unique constraint on 'WaterUsage', fields ['date', 'team']
        db.create_unique(u'resource_mgr_waterusage', ['date', 'team_id'])

        # Adding model 'WasteUsage'
        db.create_table(u'resource_mgr_wasteusage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['team_mgr.Team'])),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 11, 21, 0, 0))),
            ('time', self.gf('django.db.models.fields.TimeField')(default=datetime.time(23, 19, 22, 836630))),
            ('manual_meter_reading', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('usage', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'resource_mgr', ['WasteUsage'])

        # Adding unique constraint on 'WasteUsage', fields ['date', 'team']
        db.create_unique(u'resource_mgr_wasteusage', ['date', 'team_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'WasteUsage', fields ['date', 'team']
        db.delete_unique(u'resource_mgr_wasteusage', ['date', 'team_id'])

        # Removing unique constraint on 'WaterUsage', fields ['date', 'team']
        db.delete_unique(u'resource_mgr_waterusage', ['date', 'team_id'])

        # Removing unique constraint on 'EnergyUsage', fields ['date', 'team']
        db.delete_unique(u'resource_mgr_energyusage', ['date', 'team_id'])

        # Removing unique constraint on 'ResourceSetting', fields ['name']
        db.delete_unique(u'resource_mgr_resourcesetting', ['name'])

        # Deleting model 'ResourceSetting'
        db.delete_table(u'resource_mgr_resourcesetting')

        # Deleting model 'ResourceBlackoutDate'
        db.delete_table(u'resource_mgr_resourceblackoutdate')

        # Deleting model 'EnergyUsage'
        db.delete_table(u'resource_mgr_energyusage')

        # Deleting model 'WaterUsage'
        db.delete_table(u'resource_mgr_waterusage')

        # Deleting model 'WasteUsage'
        db.delete_table(u'resource_mgr_wasteusage')


    models = {
        u'resource_mgr.energyusage': {
            'Meta': {'ordering': "('-date', 'team')", 'unique_together': "(('date', 'team'),)", 'object_name': 'EnergyUsage'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 11, 21, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manual_meter_reading': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['team_mgr.Team']"}),
            'time': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(23, 19, 22, 836630)'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'usage': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'resource_mgr.resourceblackoutdate': {
            'Meta': {'object_name': 'ResourceBlackoutDate'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'resource_mgr.resourcesetting': {
            'Meta': {'unique_together': "(('name',),)", 'object_name': 'ResourceSetting'},
            'conversion_rate': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'winning_order': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'resource_mgr.wasteusage': {
            'Meta': {'ordering': "('-date', 'team')", 'unique_together': "(('date', 'team'),)", 'object_name': 'WasteUsage'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 11, 21, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manual_meter_reading': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['team_mgr.Team']"}),
            'time': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(23, 19, 22, 836630)'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'usage': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'resource_mgr.waterusage': {
            'Meta': {'ordering': "('-date', 'team')", 'unique_together': "(('date', 'team'),)", 'object_name': 'WaterUsage'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 11, 21, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manual_meter_reading': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['team_mgr.Team']"}),
            'time': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(23, 19, 22, 836630)'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'usage': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'team_mgr.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'team_mgr.team': {
            'Meta': {'ordering': "('group', 'name')", 'object_name': 'Team'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['team_mgr.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'size': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['resource_mgr']