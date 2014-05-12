# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'SearchField.count'
        db.add_column(u'Search_searchfield', 'count',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'SearchField.count'
        db.delete_column(u'Search_searchfield', 'count')


    models = {
        u'Search.search': {
            'Meta': {'object_name': 'Search'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'Search.searchfield': {
            'Meta': {'object_name': 'SearchField'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'field': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_list': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'search_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Search.SearchGroup']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'Search.searchgroup': {
            'Meta': {'object_name': 'SearchGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'search': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Search.Search']"})
        }
    }

    complete_apps = ['Search']