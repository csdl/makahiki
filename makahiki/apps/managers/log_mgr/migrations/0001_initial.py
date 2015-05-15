# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MakahikiLog'
        db.create_table(u'log_mgr_makahikilog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('level', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('request_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('remote_ip', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('remote_user', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=30, null=True, blank=True)),
            ('request_method', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('request_url', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('response_status', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('http_referer', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('http_user_agent', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('post_content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'log_mgr', ['MakahikiLog'])


    def backwards(self, orm):
        # Deleting model 'MakahikiLog'
        db.delete_table(u'log_mgr_makahikilog')


    models = {
        u'log_mgr.makahikilog': {
            'Meta': {'object_name': 'MakahikiLog'},
            'http_referer': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'http_user_agent': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'post_content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'remote_ip': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'remote_user': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'request_method': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'request_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'request_url': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'response_status': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['log_mgr']