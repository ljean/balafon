# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'HtmlFragment.account'
        db.delete_column('Emailing_htmlfragment', 'account_id')

        # Deleting field 'EmailImage.account'
        db.delete_column('Emailing_emailimage', 'account_id')

        # Deleting field 'EmailTemplate.account'
        db.delete_column('Emailing_emailtemplate', 'account_id')

        # Deleting field 'Emailing.account'
        db.delete_column('Emailing_emailing', 'account_id')


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'HtmlFragment.account'
        raise RuntimeError("Cannot reverse this migration. 'HtmlFragment.account' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'EmailImage.account'
        raise RuntimeError("Cannot reverse this migration. 'EmailImage.account' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'EmailTemplate.account'
        raise RuntimeError("Cannot reverse this migration. 'EmailTemplate.account' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Emailing.account'
        raise RuntimeError("Cannot reverse this migration. 'Emailing.account' and its values cannot be restored.")


    models = {
        'Crm.activitysector': {
            'Meta': {'object_name': 'ActivitySector'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'Crm.city': {
            'Meta': {'object_name': 'City'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': "''", 'to': "orm['Crm.Zone']", 'null': 'True', 'blank': 'True'})
        },
        'Crm.contact': {
            'Meta': {'object_name': 'Contact'},
            'accept_3rdparty': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'accept_newsletter': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'birth_date': ('django.db.models.fields.DateField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "u''", 'max_length': '75', 'blank': 'True'}),
            'firstname': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'main_contact': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'membership': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'contact'", 'unique': 'True', 'to': "orm['Crm.Membership']"}),
            'mobile': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'default': "u''", 'max_length': '100', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'db_index': 'True', 'blank': 'True'})
        },
        'Crm.entity': {
            'Meta': {'object_name': 'Entity'},
            'activity_sector': ('django.db.models.fields.related.ForeignKey', [], {'default': "u''", 'to': "orm['Crm.ActivitySector']", 'null': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'cedex': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'default': "u''", 'to': "orm['Crm.City']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "u''", 'max_length': '75', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'default': "u''", 'max_length': '100', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'relationship': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Crm.Relationship']"}),
            'relationship_date': ('django.db.models.fields.DateField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Crm.EntityType']"}),
            'website': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '10', 'blank': 'True'})
        },
        'Crm.entityrole': {
            'Meta': {'object_name': 'EntityRole'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'Crm.entitytype': {
            'Meta': {'object_name': 'EntityType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'Crm.membership': {
            'Meta': {'object_name': 'Membership'},
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Crm.Entity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'joining_date': ('django.db.models.fields.DateField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'leaving_date': ('django.db.models.fields.DateField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'default': "''", 'to': "orm['Crm.EntityRole']", 'null': 'True', 'blank': 'True'})
        },
        'Crm.relationship': {
            'Meta': {'object_name': 'Relationship'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'Crm.zone': {
            'Meta': {'ordering': "['name']", 'object_name': 'Zone'},
            'code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': "''", 'to': "orm['Crm.Zone']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Crm.ZoneType']"})
        },
        'Crm.zonetype': {
            'Meta': {'object_name': 'ZoneType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'Emailing.emailimage': {
            'Meta': {'object_name': 'EmailImage'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'Emailing.emailing': {
            'Meta': {'object_name': 'Emailing'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'html_content': ('html_field.db.models.fields.HTMLField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['Emailing.EmailTemplate']", 'null': 'True', 'blank': 'True'}),
            'to': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['Crm.Contact']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'Emailing.emailtemplate': {
            'Meta': {'object_name': 'EmailTemplate'},
            'body': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'Emailing.htmlfragment': {
            'Meta': {'object_name': 'HtmlFragment'},
            'content': ('html_field.db.models.fields.HTMLField', [], {'default': "''", 'blank': 'True'}),
            'div_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'Emailing.magiclink': {
            'Meta': {'object_name': 'MagicLink'},
            'emailing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Emailing.Emailing']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'db_index': 'True', 'blank': 'True'}),
            'visitors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['Crm.Contact']", 'symmetrical': 'False', 'blank': 'True'})
        }
    }

    complete_apps = ['Emailing']
