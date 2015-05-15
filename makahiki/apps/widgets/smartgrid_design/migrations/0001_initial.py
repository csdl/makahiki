# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Draft'
        db.create_table(u'smartgrid_design_draft', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
        ))
        db.send_create_signal(u'smartgrid_design', ['Draft'])

        # Adding model 'DesignerTextPromptQuestion'
        db.create_table(u'smartgrid_design_designertextpromptquestion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_design.DesignerAction'])),
            ('question', self.gf('django.db.models.fields.TextField')()),
            ('answer', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('draft', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_design.Draft'], null=True, blank=True)),
        ))
        db.send_create_signal(u'smartgrid_design', ['DesignerTextPromptQuestion'])

        # Adding model 'DesignerQuestionChoice'
        db.create_table(u'smartgrid_design_designerquestionchoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_design.DesignerTextPromptQuestion'])),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_design.DesignerAction'])),
            ('choice', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('draft', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_design.Draft'], null=True, blank=True)),
        ))
        db.send_create_signal(u'smartgrid_design', ['DesignerQuestionChoice'])

        # Adding model 'DesignerLevel'
        db.create_table(u'smartgrid_design_designerlevel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, null=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('unlock_condition', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('unlock_condition_text', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('draft', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_design.Draft'], null=True, blank=True)),
        ))
        db.send_create_signal(u'smartgrid_design', ['DesignerLevel'])

        # Adding model 'DesignerColumnName'
        db.create_table(u'smartgrid_design_designercolumnname', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, null=True)),
            ('draft', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_design.Draft'], null=True, blank=True)),
        ))
        db.send_create_signal(u'smartgrid_design', ['DesignerColumnName'])

        # Adding model 'DesignerAction'
        db.create_table(u'smartgrid_design_designeraction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
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
            ('draft', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_design.Draft'], null=True, blank=True)),
        ))
        db.send_create_signal(u'smartgrid_design', ['DesignerAction'])

        # Adding unique constraint on 'DesignerAction', fields ['slug', 'draft']
        db.create_unique(u'smartgrid_design_designeraction', ['slug', 'draft_id'])

        # Adding model 'DesignerActivity'
        db.create_table(u'smartgrid_design_designeractivity', (
            (u'designeraction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['smartgrid_design.DesignerAction'], unique=True, primary_key=True)),
            ('expected_duration', self.gf('django.db.models.fields.IntegerField')()),
            ('point_range_start', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('point_range_end', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('confirm_type', self.gf('django.db.models.fields.CharField')(default='text', max_length=20)),
            ('confirm_prompt', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('admin_note', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'smartgrid_design', ['DesignerActivity'])

        # Adding model 'DesignerCommitment'
        db.create_table(u'smartgrid_design_designercommitment', (
            (u'designeraction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['smartgrid_design.DesignerAction'], unique=True, primary_key=True)),
            ('commitment_length', self.gf('django.db.models.fields.IntegerField')(default=5)),
        ))
        db.send_create_signal(u'smartgrid_design', ['DesignerCommitment'])

        # Adding model 'DesignerEvent'
        db.create_table(u'smartgrid_design_designerevent', (
            (u'designeraction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['smartgrid_design.DesignerAction'], unique=True, primary_key=True)),
            ('expected_duration', self.gf('django.db.models.fields.IntegerField')()),
            ('event_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('event_location', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('event_max_seat', self.gf('django.db.models.fields.IntegerField')(default=1000)),
        ))
        db.send_create_signal(u'smartgrid_design', ['DesignerEvent'])

        # Adding model 'DesignerFiller'
        db.create_table(u'smartgrid_design_designerfiller', (
            (u'designeraction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['smartgrid_design.DesignerAction'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'smartgrid_design', ['DesignerFiller'])

        # Adding model 'DesignerColumnGrid'
        db.create_table(u'smartgrid_design_designercolumngrid', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_design.DesignerLevel'])),
            ('column', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_design.DesignerColumnName'])),
            ('draft', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_design.Draft'], null=True, blank=True)),
        ))
        db.send_create_signal(u'smartgrid_design', ['DesignerColumnGrid'])

        # Adding unique constraint on 'DesignerColumnGrid', fields ['level', 'name', 'draft']
        db.create_unique(u'smartgrid_design_designercolumngrid', ['level_id', 'name_id', 'draft_id'])

        # Adding model 'DesignerGrid'
        db.create_table(u'smartgrid_design_designergrid', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_design.DesignerLevel'])),
            ('column', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('row', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_design.DesignerAction'])),
            ('draft', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_design.Draft'], null=True, blank=True)),
        ))
        db.send_create_signal(u'smartgrid_design', ['DesignerGrid'])

        # Adding unique constraint on 'DesignerGrid', fields ['draft', 'level', 'column', 'row', 'action']
        db.create_unique(u'smartgrid_design_designergrid', ['draft_id', 'level_id', 'column', 'row', 'action_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'DesignerGrid', fields ['draft', 'level', 'column', 'row', 'action']
        db.delete_unique(u'smartgrid_design_designergrid', ['draft_id', 'level_id', 'column', 'row', 'action_id'])

        # Removing unique constraint on 'DesignerColumnGrid', fields ['level', 'name', 'draft']
        db.delete_unique(u'smartgrid_design_designercolumngrid', ['level_id', 'name_id', 'draft_id'])

        # Removing unique constraint on 'DesignerAction', fields ['slug', 'draft']
        db.delete_unique(u'smartgrid_design_designeraction', ['slug', 'draft_id'])

        # Deleting model 'Draft'
        db.delete_table(u'smartgrid_design_draft')

        # Deleting model 'DesignerTextPromptQuestion'
        db.delete_table(u'smartgrid_design_designertextpromptquestion')

        # Deleting model 'DesignerQuestionChoice'
        db.delete_table(u'smartgrid_design_designerquestionchoice')

        # Deleting model 'DesignerLevel'
        db.delete_table(u'smartgrid_design_designerlevel')

        # Deleting model 'DesignerColumnName'
        db.delete_table(u'smartgrid_design_designercolumnname')

        # Deleting model 'DesignerAction'
        db.delete_table(u'smartgrid_design_designeraction')

        # Deleting model 'DesignerActivity'
        db.delete_table(u'smartgrid_design_designeractivity')

        # Deleting model 'DesignerCommitment'
        db.delete_table(u'smartgrid_design_designercommitment')

        # Deleting model 'DesignerEvent'
        db.delete_table(u'smartgrid_design_designerevent')

        # Deleting model 'DesignerFiller'
        db.delete_table(u'smartgrid_design_designerfiller')

        # Deleting model 'DesignerColumnGrid'
        db.delete_table(u'smartgrid_design_designercolumngrid')

        # Deleting model 'DesignerGrid'
        db.delete_table(u'smartgrid_design_designergrid')


    models = {
        u'smartgrid_design.designeraction': {
            'Meta': {'unique_together': "(('slug', 'draft'),)", 'object_name': 'DesignerAction'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'draft': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid_design.Draft']", 'null': 'True', 'blank': 'True'}),
            'embedded_widget': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'expire_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'point_value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pub_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 11, 21, 0, 0)'}),
            'related_resource': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'social_bonus': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'unlock_condition': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'unlock_condition_text': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'video_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'video_source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'smartgrid_design.designeractivity': {
            'Meta': {'object_name': 'DesignerActivity', '_ormbases': [u'smartgrid_design.DesignerAction']},
            'admin_note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'confirm_prompt': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'confirm_type': ('django.db.models.fields.CharField', [], {'default': "'text'", 'max_length': '20'}),
            u'designeraction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['smartgrid_design.DesignerAction']", 'unique': 'True', 'primary_key': 'True'}),
            'expected_duration': ('django.db.models.fields.IntegerField', [], {}),
            'point_range_end': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'point_range_start': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'smartgrid_design.designercolumngrid': {
            'Meta': {'unique_together': "(('level', 'name', 'draft'),)", 'object_name': 'DesignerColumnGrid'},
            'column': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'draft': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid_design.Draft']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid_design.DesignerLevel']"}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid_design.DesignerColumnName']"})
        },
        u'smartgrid_design.designercolumnname': {
            'Meta': {'object_name': 'DesignerColumnName'},
            'draft': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid_design.Draft']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'null': 'True'})
        },
        u'smartgrid_design.designercommitment': {
            'Meta': {'object_name': 'DesignerCommitment', '_ormbases': [u'smartgrid_design.DesignerAction']},
            'commitment_length': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            u'designeraction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['smartgrid_design.DesignerAction']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'smartgrid_design.designerevent': {
            'Meta': {'object_name': 'DesignerEvent', '_ormbases': [u'smartgrid_design.DesignerAction']},
            u'designeraction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['smartgrid_design.DesignerAction']", 'unique': 'True', 'primary_key': 'True'}),
            'event_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'event_location': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'event_max_seat': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'expected_duration': ('django.db.models.fields.IntegerField', [], {})
        },
        u'smartgrid_design.designerfiller': {
            'Meta': {'object_name': 'DesignerFiller', '_ormbases': [u'smartgrid_design.DesignerAction']},
            u'designeraction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['smartgrid_design.DesignerAction']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'smartgrid_design.designergrid': {
            'Meta': {'ordering': "('draft', 'level', 'column', 'row')", 'unique_together': "(('draft', 'level', 'column', 'row', 'action'),)", 'object_name': 'DesignerGrid'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid_design.DesignerAction']"}),
            'column': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'draft': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid_design.Draft']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid_design.DesignerLevel']"}),
            'row': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'smartgrid_design.designerlevel': {
            'Meta': {'ordering': "('priority',)", 'object_name': 'DesignerLevel'},
            'draft': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid_design.Draft']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'null': 'True'}),
            'unlock_condition': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'unlock_condition_text': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'})
        },
        u'smartgrid_design.designerquestionchoice': {
            'Meta': {'object_name': 'DesignerQuestionChoice'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid_design.DesignerAction']"}),
            'choice': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'draft': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid_design.Draft']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid_design.DesignerTextPromptQuestion']"})
        },
        u'smartgrid_design.designertextpromptquestion': {
            'Meta': {'object_name': 'DesignerTextPromptQuestion'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid_design.DesignerAction']"}),
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'draft': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smartgrid_design.Draft']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.TextField', [], {})
        },
        u'smartgrid_design.draft': {
            'Meta': {'object_name': 'Draft'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['smartgrid_design']