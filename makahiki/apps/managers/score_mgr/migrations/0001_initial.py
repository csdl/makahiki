# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ScoreSetting'
        db.create_table(u'score_mgr_scoresetting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='Score Settings', max_length='30')),
            ('setup_points', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('active_threshold_points', self.gf('django.db.models.fields.IntegerField')(default=50)),
            ('signup_bonus_points', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('quest_bonus_points', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('noshow_penalty_points', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('feedback_bonus_points', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'score_mgr', ['ScoreSetting'])

        # Adding model 'ReferralSetting'
        db.create_table(u'score_mgr_referralsetting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('normal_referral_points', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('super_referral_points', self.gf('django.db.models.fields.IntegerField')(default=20)),
            ('mega_referral_points', self.gf('django.db.models.fields.IntegerField')(default=30)),
            ('start_dynamic_bonus', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'score_mgr', ['ReferralSetting'])

        # Adding model 'ScoreboardEntry'
        db.create_table(u'score_mgr_scoreboardentry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['player_mgr.Profile'])),
            ('round_name', self.gf('django.db.models.fields.CharField')(max_length='30')),
            ('points', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_awarded_submission', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'score_mgr', ['ScoreboardEntry'])

        # Adding unique constraint on 'ScoreboardEntry', fields ['profile', 'round_name']
        db.create_unique(u'score_mgr_scoreboardentry', ['profile_id', 'round_name'])

        # Adding model 'PointsTransaction'
        db.create_table(u'score_mgr_pointstransaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('points', self.gf('django.db.models.fields.IntegerField')()),
            ('transaction_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True)),
        ))
        db.send_create_signal(u'score_mgr', ['PointsTransaction'])

        # Adding unique constraint on 'PointsTransaction', fields ['user', 'transaction_date', 'message']
        db.create_unique(u'score_mgr_pointstransaction', ['user_id', 'transaction_date', 'message'])


    def backwards(self, orm):
        # Removing unique constraint on 'PointsTransaction', fields ['user', 'transaction_date', 'message']
        db.delete_unique(u'score_mgr_pointstransaction', ['user_id', 'transaction_date', 'message'])

        # Removing unique constraint on 'ScoreboardEntry', fields ['profile', 'round_name']
        db.delete_unique(u'score_mgr_scoreboardentry', ['profile_id', 'round_name'])

        # Deleting model 'ScoreSetting'
        db.delete_table(u'score_mgr_scoresetting')

        # Deleting model 'ReferralSetting'
        db.delete_table(u'score_mgr_referralsetting')

        # Deleting model 'ScoreboardEntry'
        db.delete_table(u'score_mgr_scoreboardentry')

        # Deleting model 'PointsTransaction'
        db.delete_table(u'score_mgr_pointstransaction')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'player_mgr.profile': {
            'Meta': {'object_name': 'Profile'},
            'completion_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'contact_carrier': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'contact_text': ('localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'daily_visit_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_ra': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_visit_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'properties': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'referrer_awarded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'referring_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'referred_profiles'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'setup_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'setup_profile': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['team_mgr.Team']", 'null': 'True', 'blank': 'True'}),
            'theme': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'profile'", 'unique': 'True', 'to': u"orm['auth.User']"})
        },
        u'score_mgr.pointstransaction': {
            'Meta': {'ordering': "('-transaction_date',)", 'unique_together': "(('user', 'transaction_date', 'message'),)", 'object_name': 'PointsTransaction'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'points': ('django.db.models.fields.IntegerField', [], {}),
            'transaction_date': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'score_mgr.referralsetting': {
            'Meta': {'object_name': 'ReferralSetting'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mega_referral_points': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'normal_referral_points': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'start_dynamic_bonus': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'super_referral_points': ('django.db.models.fields.IntegerField', [], {'default': '20'})
        },
        u'score_mgr.scoreboardentry': {
            'Meta': {'ordering': "('round_name',)", 'unique_together': "(('profile', 'round_name'),)", 'object_name': 'ScoreboardEntry'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_awarded_submission': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['player_mgr.Profile']"}),
            'round_name': ('django.db.models.fields.CharField', [], {'max_length': "'30'"})
        },
        u'score_mgr.scoresetting': {
            'Meta': {'object_name': 'ScoreSetting'},
            'active_threshold_points': ('django.db.models.fields.IntegerField', [], {'default': '50'}),
            'feedback_bonus_points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Score Settings'", 'max_length': "'30'"}),
            'noshow_penalty_points': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'quest_bonus_points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'setup_points': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'signup_bonus_points': ('django.db.models.fields.IntegerField', [], {'default': '2'})
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

    complete_apps = ['score_mgr']