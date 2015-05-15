# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ChallengeSetting'
        db.create_table(u'challenge_mgr_challengesetting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domain', self.gf('django.db.models.fields.CharField')(default='localhost', max_length=100)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=255, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='Kukui Cup', max_length=50)),
            ('theme', self.gf('django.db.models.fields.CharField')(default='theme-forest', max_length=50)),
            ('team_label', self.gf('django.db.models.fields.CharField')(default='Team', max_length=50)),
            ('use_cas_auth', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cas_server_url', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('cas_auth_text', self.gf('django.db.models.fields.TextField')(default='###I have a CAS email', max_length=255)),
            ('use_ldap_auth', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ldap_server_url', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('ldap_search_base', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('ldap_auth_text', self.gf('django.db.models.fields.TextField')(default='###I have a LDAP email', max_length=255)),
            ('use_internal_auth', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('internal_auth_text', self.gf('django.db.models.fields.TextField')(default='###Others', max_length=255)),
            ('wattdepot_server_url', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('email_enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('contact_email', self.gf('django.db.models.fields.CharField')(default='CHANGEME@example.com', max_length=100)),
            ('email_host', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('email_port', self.gf('django.db.models.fields.IntegerField')(default=587)),
            ('email_use_tls', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('landing_slogan', self.gf('django.db.models.fields.TextField')(default='The Kukui Cup: Lights off, game on!', max_length=255)),
            ('landing_introduction', self.gf('django.db.models.fields.TextField')(default='Aloha! Welcome to the Kukui Cup.', max_length=500)),
            ('landing_participant_text', self.gf('django.db.models.fields.TextField')(default='###I am registered', max_length=255)),
            ('landing_non_participant_text', self.gf('django.db.models.fields.TextField')(default='###I am not registered.', max_length=255)),
        ))
        db.send_create_signal(u'challenge_mgr', ['ChallengeSetting'])

        # Adding model 'UploadImage'
        db.create_table(u'challenge_mgr_uploadimage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'challenge_mgr', ['UploadImage'])

        # Adding model 'AboutPage'
        db.create_table(u'challenge_mgr_aboutpage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('challenge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['challenge_mgr.ChallengeSetting'])),
            ('about_page_text', self.gf('django.db.models.fields.TextField')(default="For more information, please go to <a href='http://kukuicup.org'>kukuicup.org</a>.")),
        ))
        db.send_create_signal(u'challenge_mgr', ['AboutPage'])

        # Adding model 'Sponsor'
        db.create_table(u'challenge_mgr_sponsor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('challenge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['challenge_mgr.ChallengeSetting'])),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default='1')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('logo_url', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'challenge_mgr', ['Sponsor'])

        # Adding model 'RoundSetting'
        db.create_table(u'challenge_mgr_roundsetting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='Round 1', max_length=50)),
            ('start', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 11, 21, 0, 0))),
            ('end', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 11, 28, 0, 0))),
            ('round_reset', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('display_scoreboard', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'challenge_mgr', ['RoundSetting'])

        # Adding unique constraint on 'RoundSetting', fields ['name']
        db.create_unique(u'challenge_mgr_roundsetting', ['name'])

        # Adding model 'PageInfo'
        db.create_table(u'challenge_mgr_pageinfo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('introduction', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('url', self.gf('django.db.models.fields.CharField')(default='/', max_length=255)),
            ('unlock_condition', self.gf('django.db.models.fields.CharField')(default='True', max_length=255)),
        ))
        db.send_create_signal(u'challenge_mgr', ['PageInfo'])

        # Adding model 'PageSetting'
        db.create_table(u'challenge_mgr_pagesetting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['challenge_mgr.PageInfo'])),
            ('widget', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(default='Left', max_length=10, null=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'challenge_mgr', ['PageSetting'])

        # Adding unique constraint on 'PageSetting', fields ['page', 'widget']
        db.create_unique(u'challenge_mgr_pagesetting', ['page_id', 'widget'])

        # Adding model 'GameInfo'
        db.create_table(u'challenge_mgr_gameinfo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal(u'challenge_mgr', ['GameInfo'])

        # Adding model 'GameSetting'
        db.create_table(u'challenge_mgr_gamesetting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['challenge_mgr.GameInfo'])),
            ('widget', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'challenge_mgr', ['GameSetting'])

        # Adding unique constraint on 'GameSetting', fields ['game', 'widget']
        db.create_unique(u'challenge_mgr_gamesetting', ['game_id', 'widget'])


    def backwards(self, orm):
        # Removing unique constraint on 'GameSetting', fields ['game', 'widget']
        db.delete_unique(u'challenge_mgr_gamesetting', ['game_id', 'widget'])

        # Removing unique constraint on 'PageSetting', fields ['page', 'widget']
        db.delete_unique(u'challenge_mgr_pagesetting', ['page_id', 'widget'])

        # Removing unique constraint on 'RoundSetting', fields ['name']
        db.delete_unique(u'challenge_mgr_roundsetting', ['name'])

        # Deleting model 'ChallengeSetting'
        db.delete_table(u'challenge_mgr_challengesetting')

        # Deleting model 'UploadImage'
        db.delete_table(u'challenge_mgr_uploadimage')

        # Deleting model 'AboutPage'
        db.delete_table(u'challenge_mgr_aboutpage')

        # Deleting model 'Sponsor'
        db.delete_table(u'challenge_mgr_sponsor')

        # Deleting model 'RoundSetting'
        db.delete_table(u'challenge_mgr_roundsetting')

        # Deleting model 'PageInfo'
        db.delete_table(u'challenge_mgr_pageinfo')

        # Deleting model 'PageSetting'
        db.delete_table(u'challenge_mgr_pagesetting')

        # Deleting model 'GameInfo'
        db.delete_table(u'challenge_mgr_gameinfo')

        # Deleting model 'GameSetting'
        db.delete_table(u'challenge_mgr_gamesetting')


    models = {
        u'challenge_mgr.aboutpage': {
            'Meta': {'object_name': 'AboutPage'},
            'about_page_text': ('django.db.models.fields.TextField', [], {'default': '"For more information, please go to <a href=\'http://kukuicup.org\'>kukuicup.org</a>."'}),
            'challenge': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['challenge_mgr.ChallengeSetting']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'challenge_mgr.challengesetting': {
            'Meta': {'object_name': 'ChallengeSetting'},
            'cas_auth_text': ('django.db.models.fields.TextField', [], {'default': "'###I have a CAS email'", 'max_length': '255'}),
            'cas_server_url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'contact_email': ('django.db.models.fields.CharField', [], {'default': "'CHANGEME@example.com'", 'max_length': '100'}),
            'domain': ('django.db.models.fields.CharField', [], {'default': "'localhost'", 'max_length': '100'}),
            'email_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email_host': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'email_port': ('django.db.models.fields.IntegerField', [], {'default': '587'}),
            'email_use_tls': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_auth_text': ('django.db.models.fields.TextField', [], {'default': "'###Others'", 'max_length': '255'}),
            'landing_introduction': ('django.db.models.fields.TextField', [], {'default': "'Aloha! Welcome to the Kukui Cup.'", 'max_length': '500'}),
            'landing_non_participant_text': ('django.db.models.fields.TextField', [], {'default': "'###I am not registered.'", 'max_length': '255'}),
            'landing_participant_text': ('django.db.models.fields.TextField', [], {'default': "'###I am registered'", 'max_length': '255'}),
            'landing_slogan': ('django.db.models.fields.TextField', [], {'default': "'The Kukui Cup: Lights off, game on!'", 'max_length': '255'}),
            'ldap_auth_text': ('django.db.models.fields.TextField', [], {'default': "'###I have a LDAP email'", 'max_length': '255'}),
            'ldap_search_base': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'ldap_server_url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Kukui Cup'", 'max_length': '50'}),
            'team_label': ('django.db.models.fields.CharField', [], {'default': "'Team'", 'max_length': '50'}),
            'theme': ('django.db.models.fields.CharField', [], {'default': "'theme-forest'", 'max_length': '50'}),
            'use_cas_auth': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'use_internal_auth': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'use_ldap_auth': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'wattdepot_server_url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'challenge_mgr.gameinfo': {
            'Meta': {'ordering': "['priority']", 'object_name': 'GameInfo'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'challenge_mgr.gamesetting': {
            'Meta': {'ordering': "['game', 'widget']", 'unique_together': "(('game', 'widget'),)", 'object_name': 'GameSetting'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['challenge_mgr.GameInfo']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'widget': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'challenge_mgr.pageinfo': {
            'Meta': {'ordering': "['priority']", 'object_name': 'PageInfo'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduction': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'unlock_condition': ('django.db.models.fields.CharField', [], {'default': "'True'", 'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'default': "'/'", 'max_length': '255'})
        },
        u'challenge_mgr.pagesetting': {
            'Meta': {'ordering': "['page', 'location', 'priority']", 'unique_together': "(('page', 'widget'),)", 'object_name': 'PageSetting'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "'Left'", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['challenge_mgr.PageInfo']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'widget': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        u'challenge_mgr.roundsetting': {
            'Meta': {'ordering': "['start']", 'unique_together': "(('name',),)", 'object_name': 'RoundSetting'},
            'display_scoreboard': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 11, 28, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Round 1'", 'max_length': '50'}),
            'round_reset': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 11, 21, 0, 0)'})
        },
        u'challenge_mgr.sponsor': {
            'Meta': {'ordering': "['priority', 'name']", 'object_name': 'Sponsor'},
            'challenge': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['challenge_mgr.ChallengeSetting']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'logo_url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': "'1'"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'challenge_mgr.uploadimage': {
            'Meta': {'object_name': 'UploadImage'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['challenge_mgr']