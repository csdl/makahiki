# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ParticipationSetting'
        db.create_table(u'participation_participationsetting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='Participation Settings', max_length='30')),
            ('points_50_percent', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('points_75_percent', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('points_100_percent', self.gf('django.db.models.fields.IntegerField')(default=10)),
        ))
        db.send_create_signal(u'participation', ['ParticipationSetting'])

        # Adding model 'TeamParticipation'
        db.create_table(u'participation_teamparticipation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('round_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['team_mgr.Team'])),
            ('participation', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('awarded_percent', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'participation', ['TeamParticipation'])


    def backwards(self, orm):
        # Deleting model 'ParticipationSetting'
        db.delete_table(u'participation_participationsetting')

        # Deleting model 'TeamParticipation'
        db.delete_table(u'participation_teamparticipation')


    models = {
        u'participation.participationsetting': {
            'Meta': {'object_name': 'ParticipationSetting'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Participation Settings'", 'max_length': "'30'"}),
            'points_100_percent': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'points_50_percent': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'points_75_percent': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        },
        u'participation.teamparticipation': {
            'Meta': {'ordering': "['-participation']", 'object_name': 'TeamParticipation'},
            'awarded_percent': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participation': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'round_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['team_mgr.Team']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
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

    complete_apps = ['participation']