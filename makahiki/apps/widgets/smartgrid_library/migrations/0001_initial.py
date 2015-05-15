# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LibraryTextPromptQuestion'
        db.create_table(u'smartgrid_library_librarytextpromptquestion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('libraryaction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_library.LibraryAction'])),
            ('question', self.gf('django.db.models.fields.TextField')()),
            ('answer', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'smartgrid_library', ['LibraryTextPromptQuestion'])

        # Adding model 'LibraryQuestionChoice'
        db.create_table(u'smartgrid_library_libraryquestionchoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_library.LibraryTextPromptQuestion'])),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_library.LibraryAction'])),
            ('choice', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'smartgrid_library', ['LibraryQuestionChoice'])

        # Adding model 'LibraryColumnName'
        db.create_table(u'smartgrid_library_librarycolumnname', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, null=True)),
        ))
        db.send_create_signal(u'smartgrid_library', ['LibraryColumnName'])

        # Adding model 'LibraryAction'
        db.create_table(u'smartgrid_library_libraryaction', (
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
            ('unlock_condition', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('unlock_condition_text', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('related_resource', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('social_bonus', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('point_value', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'smartgrid_library', ['LibraryAction'])

        # Adding model 'LibraryActivity'
        db.create_table(u'smartgrid_library_libraryactivity', (
            (u'libraryaction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['smartgrid_library.LibraryAction'], unique=True, primary_key=True)),
            ('expected_duration', self.gf('django.db.models.fields.IntegerField')()),
            ('point_range_start', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('point_range_end', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('confirm_type', self.gf('django.db.models.fields.CharField')(default='text', max_length=20)),
            ('confirm_prompt', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('admin_note', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'smartgrid_library', ['LibraryActivity'])

        # Adding model 'LibraryCommitment'
        db.create_table(u'smartgrid_library_librarycommitment', (
            (u'libraryaction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['smartgrid_library.LibraryAction'], unique=True, primary_key=True)),
            ('commitment_length', self.gf('django.db.models.fields.IntegerField')(default=5)),
        ))
        db.send_create_signal(u'smartgrid_library', ['LibraryCommitment'])

        # Adding model 'LibraryEvent'
        db.create_table(u'smartgrid_library_libraryevent', (
            (u'libraryaction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['smartgrid_library.LibraryAction'], unique=True, primary_key=True)),
            ('expected_duration', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'smartgrid_library', ['LibraryEvent'])


    def backwards(self, orm):
        # Deleting model 'LibraryTextPromptQuestion'
        db.delete_table(u'smartgrid_library_librarytextpromptquestion')

        # Deleting model 'LibraryQuestionChoice'
        db.delete_table(u'smartgrid_library_libraryquestionchoice')

        # Deleting model 'LibraryColumnName'
        db.delete_table(u'smartgrid_library_librarycolumnname')

        # Deleting model 'LibraryAction'
        db.delete_table(u'smartgrid_library_libraryaction')

        # Deleting model 'LibraryActivity'
        db.delete_table(u'smartgrid_library_libraryactivity')

        # Deleting model 'LibraryCommitment'
        db.delete_table(u'smartgrid_library_librarycommitment')

        # Deleting model 'LibraryEvent'
        db.delete_table(u'smartgrid_library_libraryevent')


    models = {
        u'smartgrid_library.libraryaction': {
            'Meta': {'object_name': 'LibraryAction'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'embedded_widget': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'point_value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'related_resource': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'social_bonus': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'unlock_condition': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'unlock_condition_text': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'video_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'video_source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'smartgrid_library.libraryactivity': {
            'Meta': {'object_name': 'LibraryActivity', '_ormbases': [u'smartgrid_library.LibraryAction']},
            'admin_note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'confirm_prompt': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'confirm_type': ('django.db.models.fields.CharField', [], {'default': "'text'", 'max_length': '20'}),
            'expected_duration': ('django.db.models.fields.IntegerField', [], {}),
            u'libraryaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['smartgrid_library.LibraryAction']", 'unique': 'True', 'primary_key': 'True'}),
            'point_range_end': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'point_range_start': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'smartgrid_library.librarycolumnname': {
            'Meta': {'ordering': "('name',)", 'object_name': 'LibraryColumnName'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'null': 'True'})
        },
        u'smartgrid_library.librarycommitment': {
            'Meta': {'object_name': 'LibraryCommitment', '_ormbases': [u'smartgrid_library.LibraryAction']},
            'commitment_length': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            u'libraryaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['smartgrid_library.LibraryAction']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'smartgrid_library.libraryevent': {
            'Meta': {'object_name': 'LibraryEvent', '_ormbases': [u'smartgrid_library.LibraryAction']},
            'expected_duration': ('django.db.models.fields.IntegerField', [], {}),
            u'libraryaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['smartgrid_library.LibraryAction']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'smartgrid_library.libraryquestionchoice': {
            'Meta': {'object_name': 'LibraryQuestionChoice'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid_library.LibraryAction']"}),
            'choice': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid_library.LibraryTextPromptQuestion']"})
        },
        u'smartgrid_library.librarytextpromptquestion': {
            'Meta': {'object_name': 'LibraryTextPromptQuestion'},
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'libraryaction': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid_library.LibraryAction']"}),
            'question': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['smartgrid_library']