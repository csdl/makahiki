# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EnergyGoal'
        db.create_table(u'resource_goal_energygoal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['team_mgr.Team'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('actual_usage', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('baseline_usage', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('goal_usage', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('percent_reduction', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('current_goal_percent_reduction', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('goal_status', self.gf('django.db.models.fields.CharField')(default='Not available', max_length=20)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 11, 21, 0, 0), auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'resource_goal', ['EnergyGoal'])

        # Adding unique constraint on 'EnergyGoal', fields ['date', 'team']
        db.create_unique(u'resource_goal_energygoal', ['date', 'team_id'])

        # Adding model 'WaterGoal'
        db.create_table(u'resource_goal_watergoal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['team_mgr.Team'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('actual_usage', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('baseline_usage', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('goal_usage', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('percent_reduction', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('current_goal_percent_reduction', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('goal_status', self.gf('django.db.models.fields.CharField')(default='Not available', max_length=20)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 11, 21, 0, 0), auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'resource_goal', ['WaterGoal'])

        # Adding unique constraint on 'WaterGoal', fields ['date', 'team']
        db.create_unique(u'resource_goal_watergoal', ['date', 'team_id'])

        # Adding model 'EnergyGoalSetting'
        db.create_table(u'resource_goal_energygoalsetting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['team_mgr.Team'])),
            ('goal_percent_reduction', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('baseline_method', self.gf('django.db.models.fields.CharField')(default='Dynamic', max_length=20)),
            ('data_storage', self.gf('django.db.models.fields.CharField')(default='Wattdepot', max_length=20, null=True, blank=True)),
            ('wattdepot_source_name', self.gf('django.db.models.fields.CharField')(default=None, max_length=100, null=True, blank=True)),
            ('goal_points', self.gf('django.db.models.fields.IntegerField')(default=20)),
            ('manual_entry', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('manual_entry_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('realtime_meter_interval', self.gf('django.db.models.fields.IntegerField')(default=10)),
        ))
        db.send_create_signal(u'resource_goal', ['EnergyGoalSetting'])

        # Adding unique constraint on 'EnergyGoalSetting', fields ['team']
        db.create_unique(u'resource_goal_energygoalsetting', ['team_id'])

        # Adding model 'WaterGoalSetting'
        db.create_table(u'resource_goal_watergoalsetting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['team_mgr.Team'])),
            ('goal_percent_reduction', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('baseline_method', self.gf('django.db.models.fields.CharField')(default='Dynamic', max_length=20)),
            ('data_storage', self.gf('django.db.models.fields.CharField')(default='Wattdepot', max_length=20, null=True, blank=True)),
            ('wattdepot_source_name', self.gf('django.db.models.fields.CharField')(default=None, max_length=100, null=True, blank=True)),
            ('goal_points', self.gf('django.db.models.fields.IntegerField')(default=20)),
            ('manual_entry', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('manual_entry_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('realtime_meter_interval', self.gf('django.db.models.fields.IntegerField')(default=10)),
        ))
        db.send_create_signal(u'resource_goal', ['WaterGoalSetting'])

        # Adding unique constraint on 'WaterGoalSetting', fields ['team']
        db.create_unique(u'resource_goal_watergoalsetting', ['team_id'])

        # Adding model 'EnergyBaselineDaily'
        db.create_table(u'resource_goal_energybaselinedaily', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['team_mgr.Team'])),
            ('day', self.gf('django.db.models.fields.IntegerField')()),
            ('usage', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'resource_goal', ['EnergyBaselineDaily'])

        # Adding model 'WaterBaselineDaily'
        db.create_table(u'resource_goal_waterbaselinedaily', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['team_mgr.Team'])),
            ('day', self.gf('django.db.models.fields.IntegerField')()),
            ('usage', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'resource_goal', ['WaterBaselineDaily'])

        # Adding model 'EnergyBaselineHourly'
        db.create_table(u'resource_goal_energybaselinehourly', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['team_mgr.Team'])),
            ('day', self.gf('django.db.models.fields.IntegerField')()),
            ('hour', self.gf('django.db.models.fields.IntegerField')()),
            ('usage', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'resource_goal', ['EnergyBaselineHourly'])

        # Adding model 'WaterBaselineHourly'
        db.create_table(u'resource_goal_waterbaselinehourly', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['team_mgr.Team'])),
            ('day', self.gf('django.db.models.fields.IntegerField')()),
            ('hour', self.gf('django.db.models.fields.IntegerField')()),
            ('usage', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'resource_goal', ['WaterBaselineHourly'])


    def backwards(self, orm):
        # Removing unique constraint on 'WaterGoalSetting', fields ['team']
        db.delete_unique(u'resource_goal_watergoalsetting', ['team_id'])

        # Removing unique constraint on 'EnergyGoalSetting', fields ['team']
        db.delete_unique(u'resource_goal_energygoalsetting', ['team_id'])

        # Removing unique constraint on 'WaterGoal', fields ['date', 'team']
        db.delete_unique(u'resource_goal_watergoal', ['date', 'team_id'])

        # Removing unique constraint on 'EnergyGoal', fields ['date', 'team']
        db.delete_unique(u'resource_goal_energygoal', ['date', 'team_id'])

        # Deleting model 'EnergyGoal'
        db.delete_table(u'resource_goal_energygoal')

        # Deleting model 'WaterGoal'
        db.delete_table(u'resource_goal_watergoal')

        # Deleting model 'EnergyGoalSetting'
        db.delete_table(u'resource_goal_energygoalsetting')

        # Deleting model 'WaterGoalSetting'
        db.delete_table(u'resource_goal_watergoalsetting')

        # Deleting model 'EnergyBaselineDaily'
        db.delete_table(u'resource_goal_energybaselinedaily')

        # Deleting model 'WaterBaselineDaily'
        db.delete_table(u'resource_goal_waterbaselinedaily')

        # Deleting model 'EnergyBaselineHourly'
        db.delete_table(u'resource_goal_energybaselinehourly')

        # Deleting model 'WaterBaselineHourly'
        db.delete_table(u'resource_goal_waterbaselinehourly')


    models = {
        u'resource_goal.energybaselinedaily': {
            'Meta': {'object_name': 'EnergyBaselineDaily'},
            'day': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['team_mgr.Team']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'usage': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'resource_goal.energybaselinehourly': {
            'Meta': {'object_name': 'EnergyBaselineHourly'},
            'day': ('django.db.models.fields.IntegerField', [], {}),
            'hour': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['team_mgr.Team']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'usage': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'resource_goal.energygoal': {
            'Meta': {'ordering': "('-date', 'team')", 'unique_together': "(('date', 'team'),)", 'object_name': 'EnergyGoal'},
            'actual_usage': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'baseline_usage': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'current_goal_percent_reduction': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'goal_status': ('django.db.models.fields.CharField', [], {'default': "'Not available'", 'max_length': '20'}),
            'goal_usage': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent_reduction': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['team_mgr.Team']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 11, 21, 0, 0)', 'auto_now': 'True', 'blank': 'True'})
        },
        u'resource_goal.energygoalsetting': {
            'Meta': {'ordering': "('team',)", 'unique_together': "(('team',),)", 'object_name': 'EnergyGoalSetting'},
            'baseline_method': ('django.db.models.fields.CharField', [], {'default': "'Dynamic'", 'max_length': '20'}),
            'data_storage': ('django.db.models.fields.CharField', [], {'default': "'Wattdepot'", 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'goal_percent_reduction': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'goal_points': ('django.db.models.fields.IntegerField', [], {'default': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manual_entry': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manual_entry_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'realtime_meter_interval': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['team_mgr.Team']"}),
            'wattdepot_source_name': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'resource_goal.waterbaselinedaily': {
            'Meta': {'object_name': 'WaterBaselineDaily'},
            'day': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['team_mgr.Team']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'usage': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'resource_goal.waterbaselinehourly': {
            'Meta': {'object_name': 'WaterBaselineHourly'},
            'day': ('django.db.models.fields.IntegerField', [], {}),
            'hour': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['team_mgr.Team']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'usage': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'resource_goal.watergoal': {
            'Meta': {'ordering': "('-date', 'team')", 'unique_together': "(('date', 'team'),)", 'object_name': 'WaterGoal'},
            'actual_usage': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'baseline_usage': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'current_goal_percent_reduction': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'goal_status': ('django.db.models.fields.CharField', [], {'default': "'Not available'", 'max_length': '20'}),
            'goal_usage': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent_reduction': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['team_mgr.Team']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 11, 21, 0, 0)', 'auto_now': 'True', 'blank': 'True'})
        },
        u'resource_goal.watergoalsetting': {
            'Meta': {'ordering': "('team',)", 'unique_together': "(('team',),)", 'object_name': 'WaterGoalSetting'},
            'baseline_method': ('django.db.models.fields.CharField', [], {'default': "'Dynamic'", 'max_length': '20'}),
            'data_storage': ('django.db.models.fields.CharField', [], {'default': "'Wattdepot'", 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'goal_percent_reduction': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'goal_points': ('django.db.models.fields.IntegerField', [], {'default': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manual_entry': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manual_entry_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'realtime_meter_interval': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['team_mgr.Team']"}),
            'wattdepot_source_name': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'})
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

    complete_apps = ['resource_goal']