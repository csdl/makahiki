# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HelpTopic'
        db.create_table(u'help_helptopic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('contents', self.gf('django.db.models.fields.TextField')()),
            ('parent_topic', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='sub_topics', null=True, to=orm['help.HelpTopic'])),
        ))
        db.send_create_signal(u'help', ['HelpTopic'])


    def backwards(self, orm):
        # Deleting model 'HelpTopic'
        db.delete_table(u'help_helptopic')


    models = {
        u'help.helptopic': {
            'Meta': {'ordering': "['category', 'priority']", 'object_name': 'HelpTopic'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'contents': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_topic': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sub_topics'", 'null': 'True', 'to': u"orm['help.HelpTopic']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['help']