# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TextPromptQuestion'
        db.create_table(u'smartgrid_textpromptquestion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid.Action'])),
            ('question', self.gf('django.db.models.fields.TextField')()),
            ('answer', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'smartgrid', ['TextPromptQuestion'])

        # Adding model 'QuestionChoice'
        db.create_table(u'smartgrid_questionchoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid.TextPromptQuestion'])),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid.Action'])),
            ('choice', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'smartgrid', ['QuestionChoice'])

        # Adding model 'Level'
        db.create_table(u'smartgrid_level', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, null=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('unlock_condition', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('unlock_condition_text', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
        ))
        db.send_create_signal(u'smartgrid', ['Level'])

        # Adding model 'ColumnName'
        db.create_table(u'smartgrid_columnname', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, null=True)),
        ))
        db.send_create_signal(u'smartgrid', ['ColumnName'])

        # Adding model 'Action'
        db.create_table(u'smartgrid_action', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=255, null=True, blank=True)),
            ('video_id', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('video_source', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('embedded_widget', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('pub_date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 11, 21, 0, 0))),
            ('expire_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('unlock_condition', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('unlock_condition_text', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('related_resource', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('social_bonus', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('point_value', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'smartgrid', ['Action'])

        # Adding model 'Activity'
        db.create_table(u'smartgrid_activity', (
            (u'action_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['smartgrid.Action'], unique=True, primary_key=True)),
            ('expected_duration', self.gf('django.db.models.fields.IntegerField')()),
            ('point_range_start', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('point_range_end', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('confirm_type', self.gf('django.db.models.fields.CharField')(default='text', max_length=20)),
            ('confirm_prompt', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('admin_note', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'smartgrid', ['Activity'])

        # Adding model 'Commitment'
        db.create_table(u'smartgrid_commitment', (
            (u'action_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['smartgrid.Action'], unique=True, primary_key=True)),
            ('commitment_length', self.gf('django.db.models.fields.IntegerField')(default=5)),
        ))
        db.send_create_signal(u'smartgrid', ['Commitment'])

        # Adding model 'Event'
        db.create_table(u'smartgrid_event', (
            (u'action_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['smartgrid.Action'], unique=True, primary_key=True)),
            ('expected_duration', self.gf('django.db.models.fields.IntegerField')()),
            ('event_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('event_location', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('event_max_seat', self.gf('django.db.models.fields.IntegerField')(default=1000)),
        ))
        db.send_create_signal(u'smartgrid', ['Event'])

        # Adding model 'Filler'
        db.create_table(u'smartgrid_filler', (
            (u'action_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['smartgrid.Action'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'smartgrid', ['Filler'])

        # Adding model 'ColumnGrid'
        db.create_table(u'smartgrid_columngrid', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid.Level'])),
            ('column', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid.ColumnName'])),
        ))
        db.send_create_signal(u'smartgrid', ['ColumnGrid'])

        # Adding model 'Grid'
        db.create_table(u'smartgrid_grid', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid.Level'])),
            ('column', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('row', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid.Action'])),
        ))
        db.send_create_signal(u'smartgrid', ['Grid'])

        # Adding model 'ActionMember'
        db.create_table(u'smartgrid_actionmember', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid.Action'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid.TextPromptQuestion'], null=True, blank=True)),
            ('submission_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('completion_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('award_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('approval_status', self.gf('django.db.models.fields.CharField')(default='pending', max_length=20)),
            ('social_bonus_awarded', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('social_email', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('response', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('admin_comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=1024, blank=True)),
            ('points_awarded', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('admin_link', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'smartgrid', ['ActionMember'])

        # Adding unique constraint on 'ActionMember', fields ['user', 'action', 'submission_date']
        db.create_unique(u'smartgrid_actionmember', ['user_id', 'action_id', 'submission_date'])

        # Adding model 'EmailReminder'
        db.create_table(u'smartgrid_emailreminder', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid.Action'])),
            ('send_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('email_address', self.gf('django.db.models.fields.EmailField')(max_length=75)),
        ))
        db.send_create_signal(u'smartgrid', ['EmailReminder'])

        # Adding unique constraint on 'EmailReminder', fields ['user', 'action']
        db.create_unique(u'smartgrid_emailreminder', ['user_id', 'action_id'])

        # Adding model 'TextReminder'
        db.create_table(u'smartgrid_textreminder', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid.Action'])),
            ('send_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('text_number', self.gf('localflavor.us.models.PhoneNumberField')(max_length=20)),
            ('text_carrier', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal(u'smartgrid', ['TextReminder'])

        # Adding unique constraint on 'TextReminder', fields ['user', 'action']
        db.create_unique(u'smartgrid_textreminder', ['user_id', 'action_id'])

        # Adding model 'ConfirmationCode'
        db.create_table(u'smartgrid_confirmationcode', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid.Action'])),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50, db_index=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 11, 21, 0, 0))),
            ('printed_or_distributed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'smartgrid', ['ConfirmationCode'])


    def backwards(self, orm):
        # Removing unique constraint on 'TextReminder', fields ['user', 'action']
        db.delete_unique(u'smartgrid_textreminder', ['user_id', 'action_id'])

        # Removing unique constraint on 'EmailReminder', fields ['user', 'action']
        db.delete_unique(u'smartgrid_emailreminder', ['user_id', 'action_id'])

        # Removing unique constraint on 'ActionMember', fields ['user', 'action', 'submission_date']
        db.delete_unique(u'smartgrid_actionmember', ['user_id', 'action_id', 'submission_date'])

        # Deleting model 'TextPromptQuestion'
        db.delete_table(u'smartgrid_textpromptquestion')

        # Deleting model 'QuestionChoice'
        db.delete_table(u'smartgrid_questionchoice')

        # Deleting model 'Level'
        db.delete_table(u'smartgrid_level')

        # Deleting model 'ColumnName'
        db.delete_table(u'smartgrid_columnname')

        # Deleting model 'Action'
        db.delete_table(u'smartgrid_action')

        # Deleting model 'Activity'
        db.delete_table(u'smartgrid_activity')

        # Deleting model 'Commitment'
        db.delete_table(u'smartgrid_commitment')

        # Deleting model 'Event'
        db.delete_table(u'smartgrid_event')

        # Deleting model 'Filler'
        db.delete_table(u'smartgrid_filler')

        # Deleting model 'ColumnGrid'
        db.delete_table(u'smartgrid_columngrid')

        # Deleting model 'Grid'
        db.delete_table(u'smartgrid_grid')

        # Deleting model 'ActionMember'
        db.delete_table(u'smartgrid_actionmember')

        # Deleting model 'EmailReminder'
        db.delete_table(u'smartgrid_emailreminder')

        # Deleting model 'TextReminder'
        db.delete_table(u'smartgrid_textreminder')

        # Deleting model 'ConfirmationCode'
        db.delete_table(u'smartgrid_confirmationcode')


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
        u'smartgrid.action': {
            'Meta': {'object_name': 'Action'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'embedded_widget': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'expire_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'point_value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pub_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 11, 21, 0, 0)'}),
            'related_resource': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'social_bonus': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'unlock_condition': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'unlock_condition_text': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'through': u"orm['smartgrid.ActionMember']", 'symmetrical': 'False'}),
            'video_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'video_source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'smartgrid.actionmember': {
            'Meta': {'unique_together': "(('user', 'action', 'submission_date'),)", 'object_name': 'ActionMember'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid.Action']"}),
            'admin_comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'admin_link': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'approval_status': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '20'}),
            'award_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'completion_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '1024', 'blank': 'True'}),
            'points_awarded': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid.TextPromptQuestion']", 'null': 'True', 'blank': 'True'}),
            'response': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'social_bonus_awarded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'social_email': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'submission_date': ('django.db.models.fields.DateTimeField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'smartgrid.activity': {
            'Meta': {'object_name': 'Activity', '_ormbases': [u'smartgrid.Action']},
            u'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['smartgrid.Action']", 'unique': 'True', 'primary_key': 'True'}),
            'admin_note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'confirm_prompt': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'confirm_type': ('django.db.models.fields.CharField', [], {'default': "'text'", 'max_length': '20'}),
            'expected_duration': ('django.db.models.fields.IntegerField', [], {}),
            'point_range_end': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'point_range_start': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'smartgrid.columngrid': {
            'Meta': {'object_name': 'ColumnGrid'},
            'column': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid.Level']"}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid.ColumnName']"})
        },
        u'smartgrid.columnname': {
            'Meta': {'object_name': 'ColumnName'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'null': 'True'})
        },
        u'smartgrid.commitment': {
            'Meta': {'object_name': 'Commitment', '_ormbases': [u'smartgrid.Action']},
            u'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['smartgrid.Action']", 'unique': 'True', 'primary_key': 'True'}),
            'commitment_length': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        },
        u'smartgrid.confirmationcode': {
            'Meta': {'object_name': 'ConfirmationCode'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid.Action']"}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 11, 21, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'printed_or_distributed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'smartgrid.emailreminder': {
            'Meta': {'unique_together': "(('user', 'action'),)", 'object_name': 'EmailReminder'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid.Action']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'send_at': ('django.db.models.fields.DateTimeField', [], {}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'smartgrid.event': {
            'Meta': {'object_name': 'Event', '_ormbases': [u'smartgrid.Action']},
            u'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['smartgrid.Action']", 'unique': 'True', 'primary_key': 'True'}),
            'event_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'event_location': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'event_max_seat': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'expected_duration': ('django.db.models.fields.IntegerField', [], {})
        },
        u'smartgrid.filler': {
            'Meta': {'object_name': 'Filler', '_ormbases': [u'smartgrid.Action']},
            u'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['smartgrid.Action']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'smartgrid.grid': {
            'Meta': {'ordering': "('level', 'column', 'row')", 'object_name': 'Grid'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid.Action']"}),
            'column': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid.Level']"}),
            'row': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'smartgrid.level': {
            'Meta': {'ordering': "('priority',)", 'object_name': 'Level'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'null': 'True'}),
            'unlock_condition': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'unlock_condition_text': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'})
        },
        u'smartgrid.questionchoice': {
            'Meta': {'object_name': 'QuestionChoice'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid.Action']"}),
            'choice': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid.TextPromptQuestion']"})
        },
        u'smartgrid.textpromptquestion': {
            'Meta': {'object_name': 'TextPromptQuestion'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid.Action']"}),
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.TextField', [], {})
        },
        u'smartgrid.textreminder': {
            'Meta': {'unique_together': "(('user', 'action'),)", 'object_name': 'TextReminder'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid.Action']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'send_at': ('django.db.models.fields.DateTimeField', [], {}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text_carrier': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'text_number': ('localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['smartgrid']