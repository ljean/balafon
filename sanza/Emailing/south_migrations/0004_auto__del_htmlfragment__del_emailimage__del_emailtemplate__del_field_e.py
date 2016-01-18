# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'HtmlFragment'
        db.delete_table('Emailing_htmlfragment')

        # Deleting model 'EmailImage'
        db.delete_table('Emailing_emailimage')

        # Deleting model 'EmailTemplate'
        db.delete_table('Emailing_emailtemplate')

        # Deleting field 'Emailing.sent_at'
        db.delete_column('Emailing_emailing', 'sent_at')

        # Deleting field 'Emailing.template'
        db.delete_column('Emailing_emailing', 'template_id')

        # Deleting field 'Emailing.html_content'
        db.delete_column('Emailing_emailing', 'html_content')

        # Deleting field 'Emailing.subject'
        db.delete_column('Emailing_emailing', 'subject')

        # Adding field 'Emailing.newsletter'
        db.add_column('Emailing_emailing', 'newsletter', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['coop_cms.Newsletter']), keep_default=False)

        # Adding field 'Emailing.status'
        db.add_column('Emailing_emailing', 'status', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)

        # Adding field 'Emailing.scheduling_dt'
        db.add_column('Emailing_emailing', 'scheduling_dt', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True), keep_default=False)

        # Adding field 'Emailing.sending_dt'
        db.add_column('Emailing_emailing', 'sending_dt', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding model 'HtmlFragment'
        db.create_table('Emailing_htmlfragment', (
            ('content', self.gf('html_field.db.models.fields.HTMLField')(default='', blank=True)),
            ('div_id', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('Emailing', ['HtmlFragment'])

        # Adding model 'EmailImage'
        db.create_table('Emailing_emailimage', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('Emailing', ['EmailImage'])

        # Adding model 'EmailTemplate'
        db.create_table('Emailing_emailtemplate', (
            ('body', self.gf('django.db.models.fields.TextField')(default='', max_length=100, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('Emailing', ['EmailTemplate'])

        # Adding field 'Emailing.sent_at'
        db.add_column('Emailing_emailing', 'sent_at', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True), keep_default=False)

        # Adding field 'Emailing.template'
        db.add_column('Emailing_emailing', 'template', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['Emailing.EmailTemplate'], null=True, blank=True), keep_default=False)

        # Adding field 'Emailing.html_content'
        db.add_column('Emailing_emailing', 'html_content', self.gf('html_field.db.models.fields.HTMLField')(default='', blank=True), keep_default=False)

        # User chose to not deal with backwards NULL issues for 'Emailing.subject'
        raise RuntimeError("Cannot reverse this migration. 'Emailing.subject' and its values cannot be restored.")

        # Deleting field 'Emailing.newsletter'
        db.delete_column('Emailing_emailing', 'newsletter_id')

        # Deleting field 'Emailing.status'
        db.delete_column('Emailing_emailing', 'status')

        # Deleting field 'Emailing.scheduling_dt'
        db.delete_column('Emailing_emailing', 'scheduling_dt')

        # Deleting field 'Emailing.sending_dt'
        db.delete_column('Emailing_emailing', 'sending_dt')


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
            'address': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'birth_date': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'cedex': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'default': "u''", 'to': "orm['Crm.City']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "u''", 'max_length': '75', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Crm.Entity']"}),
            'firstname': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'has_left': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'main_contact': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'mobile': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'default': "u''", 'max_length': '100', 'blank': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['Crm.EntityRole']", 'null': 'True', 'blank': 'True'}),
            'same_as': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['Crm.SameAs']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'db_index': 'True', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '10', 'blank': 'True'})
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
            'relationship_date': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
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
        'Crm.relationship': {
            'Meta': {'object_name': 'Relationship'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'Crm.sameas': {
            'Meta': {'object_name': 'SameAs'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
        'Emailing.emailing': {
            'Meta': {'object_name': 'Emailing'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'newsletter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coop_cms.Newsletter']"}),
            'scheduling_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'sending_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'to': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['Crm.Contact']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'Emailing.magiclink': {
            'Meta': {'object_name': 'MagicLink'},
            'emailing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Emailing.Emailing']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'db_index': 'True', 'blank': 'True'}),
            'visitors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['Crm.Contact']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'coop_cms.newsletter': {
            'Meta': {'object_name': 'Newsletter'},
            'content': ('html_field.db.models.fields.HTMLField', [], {'default': "'<br>'", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['coop_cms.NewsletterItem']", 'symmetrical': 'False', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'template': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        },
        'coop_cms.newsletteritem': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'NewsletterItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['Emailing']
