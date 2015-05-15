# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Prize'
        db.create_table(u'prizes_prize', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['challenge_mgr.RoundSetting'], null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('short_description', self.gf('django.db.models.fields.TextField')()),
            ('long_description', self.gf('django.db.models.fields.TextField')()),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=1024, blank=True)),
            ('award_to', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('competition_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'prizes', ['Prize'])

        # Adding unique constraint on 'Prize', fields ['round', 'award_to', 'competition_type']
        db.create_unique(u'prizes_prize', ['round_id', 'award_to', 'competition_type'])


    def backwards(self, orm):
        # Removing unique constraint on 'Prize', fields ['round', 'award_to', 'competition_type']
        db.delete_unique(u'prizes_prize', ['round_id', 'award_to', 'competition_type'])

        # Deleting model 'Prize'
        db.delete_table(u'prizes_prize')


    models = {
        u'challenge_mgr.roundsetting': {
            'Meta': {'ordering': "['start']", 'unique_together': "(('name',),)", 'object_name': 'RoundSetting'},
            'display_scoreboard': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 11, 28, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Round 1'", 'max_length': '50'}),
            'round_reset': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 11, 21, 0, 0)'})
        },
        u'prizes.prize': {
            'Meta': {'ordering': "('round__name', 'award_to', 'competition_type')", 'unique_together': "(('round', 'award_to', 'competition_type'),)", 'object_name': 'Prize'},
            'award_to': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'competition_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '1024', 'blank': 'True'}),
            'long_description': ('django.db.models.fields.TextField', [], {}),
            'round': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['challenge_mgr.RoundSetting']", 'null': 'True', 'blank': 'True'}),
            'short_description': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['prizes']