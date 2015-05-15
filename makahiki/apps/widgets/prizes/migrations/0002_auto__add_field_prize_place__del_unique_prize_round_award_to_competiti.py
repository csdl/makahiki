# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Prize', fields ['round', 'award_to', 'competition_type']
        db.delete_unique(u'prizes_prize', ['round_id', 'award_to', 'competition_type'])

        # Adding field 'Prize.place'
        db.add_column(u'prizes_prize', 'place',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Adding unique constraint on 'Prize', fields ['round', 'award_to', 'competition_type', 'place']
        db.create_unique(u'prizes_prize', ['round_id', 'award_to', 'competition_type', 'place'])


    def backwards(self, orm):
        # Removing unique constraint on 'Prize', fields ['round', 'award_to', 'competition_type', 'place']
        db.delete_unique(u'prizes_prize', ['round_id', 'award_to', 'competition_type', 'place'])

        # Deleting field 'Prize.place'
        db.delete_column(u'prizes_prize', 'place')

        # Adding unique constraint on 'Prize', fields ['round', 'award_to', 'competition_type']
        db.create_unique(u'prizes_prize', ['round_id', 'award_to', 'competition_type'])


    models = {
        u'challenge_mgr.roundsetting': {
            'Meta': {'ordering': "['start']", 'unique_together': "(('name',),)", 'object_name': 'RoundSetting'},
            'display_scoreboard': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 1, 31, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Round 1'", 'max_length': '50'}),
            'round_reset': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 1, 24, 0, 0)'})
        },
        u'prizes.prize': {
            'Meta': {'ordering': "('round__name', 'award_to', 'competition_type', 'place')", 'unique_together': "(('round', 'award_to', 'competition_type', 'place'),)", 'object_name': 'Prize'},
            'award_to': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'competition_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '1024', 'blank': 'True'}),
            'long_description': ('django.db.models.fields.TextField', [], {}),
            'place': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'round': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['challenge_mgr.RoundSetting']", 'null': 'True', 'blank': 'True'}),
            'short_description': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['prizes']