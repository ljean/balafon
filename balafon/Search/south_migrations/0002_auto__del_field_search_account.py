# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Search.account'
        db.delete_column('Search_search', 'account_id')


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'Search.account'
        raise RuntimeError("Cannot reverse this migration. 'Search.account' and its values cannot be restored.")


    models = {
        'Search.search': {
            'Meta': {'object_name': 'Search'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'Search.searchfield': {
            'Meta': {'object_name': 'SearchField'},
            'field': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'search_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Search.SearchGroup']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'Search.searchgroup': {
            'Meta': {'object_name': 'SearchGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'search': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Search.Search']"})
        }
    }

    complete_apps = ['Search']
