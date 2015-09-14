# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PricePolicy'
        db.create_table(u'Store_pricepolicy', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('parameters', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('policy', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('apply_to', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'Store', ['PricePolicy'])

        # Adding field 'StoreItem.price_policy'
        db.add_column(u'Store_storeitem', 'price_policy',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['Store.PricePolicy'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'StoreItemCategory.parent'
        db.add_column(u'Store_storeitemcategory', 'parent',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='subcategories_set', null=True, blank=True, to=orm['Store.StoreItemCategory']),
                      keep_default=False)

        # Adding field 'StoreItemCategory.price_policy'
        db.add_column(u'Store_storeitemcategory', 'price_policy',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['Store.PricePolicy'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'PricePolicy'
        db.delete_table(u'Store_pricepolicy')

        # Deleting field 'StoreItem.price_policy'
        db.delete_column(u'Store_storeitem', 'price_policy_id')

        # Deleting field 'StoreItemCategory.parent'
        db.delete_column(u'Store_storeitemcategory', 'parent_id')

        # Deleting field 'StoreItemCategory.price_policy'
        db.delete_column(u'Store_storeitemcategory', 'price_policy_id')


    models = {
        u'Crm.action': {
            'Meta': {'object_name': 'Action'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': 'None', 'null': 'True', 'max_digits': '11', 'decimal_places': '2', 'blank': 'True'}),
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': u"orm['Crm.Contact']", 'null': 'True', 'symmetrical': 'False', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'detail': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'display_on_board': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'done_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'end_datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'entities': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': u"orm['Crm.Entity']", 'null': 'True', 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_charge': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Crm.TeamMember']", 'null': 'True', 'blank': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'opportunity': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Crm.Opportunity']", 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Crm.Action']", 'null': 'True', 'blank': 'True'}),
            'planned_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Crm.ActionStatus']", 'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Crm.ActionType']", 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'db_index': 'True', 'blank': 'True'})
        },
        u'Crm.actionset': {
            'Meta': {'ordering': "['ordering']", 'object_name': 'ActionSet'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '10'})
        },
        u'Crm.actionstatus': {
            'Meta': {'ordering': "['ordering']", 'object_name': 'ActionStatus'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '10'})
        },
        u'Crm.actiontype': {
            'Meta': {'ordering': "['order_index', 'name']", 'object_name': 'ActionType'},
            'action_template': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'allowed_status': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': u"orm['Crm.ActionStatus']", 'null': 'True', 'symmetrical': 'False', 'blank': 'True'}),
            'default_status': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'type_default_status_set'", 'null': 'True', 'blank': 'True', 'to': u"orm['Crm.ActionStatus']"}),
            'default_template': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'generate_uuid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_amount_calculated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_editable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'next_action_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['Crm.ActionType']", 'symmetrical': 'False', 'blank': 'True'}),
            'not_assigned_when_cloned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'number_auto_generated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'order_index': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'set': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Crm.ActionSet']", 'null': 'True', 'blank': 'True'}),
            'subscribe_form': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'Crm.city': {
            'Meta': {'ordering': "['name']", 'object_name': 'City'},
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'city_groups_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['Crm.Zone']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Crm.Zone']", 'null': 'True', 'blank': 'True'})
        },
        u'Crm.contact': {
            'Meta': {'ordering': "('lastname', 'firstname')", 'object_name': 'Contact'},
            'accept_notifications': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'address3': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'birth_date': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'cedex': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Crm.City']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "u''", 'max_length': '75', 'blank': 'True'}),
            'email_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Crm.Entity']"}),
            'favorite_language': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'}),
            'firstname': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'has_left': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Crm.ContactsImport']", 'null': 'True', 'blank': 'True'}),
            'job': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'db_index': 'True', 'blank': 'True'}),
            'main_contact': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'mobile': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'default': "u''", 'max_length': '100', 'blank': 'True'}),
            'relationships': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': u"orm['Crm.Contact']", 'through': u"orm['Crm.Relationship']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'role': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': u"orm['Crm.EntityRole']", 'null': 'True', 'symmetrical': 'False', 'blank': 'True'}),
            'same_as': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Crm.SameAs']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'db_index': 'True', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '20', 'blank': 'True'})
        },
        u'Crm.contactsimport': {
            'Meta': {'object_name': 'ContactsImport'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'encoding': ('django.db.models.fields.CharField', [], {'default': "'utf-8'", 'max_length': '50'}),
            'entity_name_from_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'entity_type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Crm.EntityType']", 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': u"orm['Crm.Group']", 'null': 'True', 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'imported_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '100', 'blank': 'True'}),
            'separator': ('django.db.models.fields.CharField', [], {'default': "','", 'max_length': '5'})
        },
        u'Crm.entity': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Entity'},
            'address': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'address3': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'cedex': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Crm.City']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "u''", 'max_length': '75', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Crm.ContactsImport']", 'null': 'True', 'blank': 'True'}),
            'is_single_contact': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'default': "u''", 'max_length': '100', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'relationship_date': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Crm.EntityType']", 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '20', 'blank': 'True'})
        },
        u'Crm.entityrole': {
            'Meta': {'object_name': 'EntityRole'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'Crm.entitytype': {
            'Meta': {'ordering': "['order']", 'object_name': 'EntityType'},
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'default': "u''", 'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subscribe_form': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'Crm.group': {
            'Meta': {'object_name': 'Group'},
            'background_color': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '7', 'blank': 'True'}),
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['Crm.Contact']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'entities': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['Crm.Entity']", 'null': 'True', 'blank': 'True'}),
            'fore_color': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '7', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'subscribe_form': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'Crm.opportunity': {
            'Meta': {'object_name': 'Opportunity'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': 'None', 'null': 'True', 'max_digits': '11', 'decimal_places': '2', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'detail': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'display_on_board': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'ended': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Crm.Entity']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'probability': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'start_date': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Crm.OpportunityStatus']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Crm.OpportunityType']", 'null': 'True', 'blank': 'True'})
        },
        u'Crm.opportunitystatus': {
            'Meta': {'object_name': 'OpportunityStatus'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'Crm.opportunitytype': {
            'Meta': {'object_name': 'OpportunityType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'Crm.relationship': {
            'Meta': {'object_name': 'Relationship'},
            'contact1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'relationships1'", 'to': u"orm['Crm.Contact']"}),
            'contact2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'relationships2'", 'to': u"orm['Crm.Contact']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'relationship_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Crm.RelationshipType']"})
        },
        u'Crm.relationshiptype': {
            'Meta': {'object_name': 'RelationshipType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'reverse': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'})
        },
        u'Crm.sameas': {
            'Meta': {'object_name': 'SameAs'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_contact': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Crm.Contact']", 'null': 'True', 'blank': 'True'})
        },
        u'Crm.teammember': {
            'Meta': {'object_name': 'TeamMember'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'default': 'None', 'to': u"orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'Crm.zone': {
            'Meta': {'ordering': "['name']", 'object_name': 'Zone'},
            'code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Crm.Zone']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Crm.ZoneType']"})
        },
        u'Crm.zonetype': {
            'Meta': {'object_name': 'ZoneType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'Store.brand': {
            'Meta': {'object_name': 'Brand'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'Store.deliverypoint': {
            'Meta': {'ordering': "('name',)", 'object_name': 'DeliveryPoint'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'Store.pricepolicy': {
            'Meta': {'object_name': 'PricePolicy'},
            'apply_to': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parameters': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'policy': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'Store.sale': {
            'Meta': {'object_name': 'Sale'},
            'action': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['Crm.Action']", 'unique': 'True'}),
            'delivery_point': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Store.DeliveryPoint']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'Store.saleitem': {
            'Meta': {'ordering': "['order_index']", 'object_name': 'SaleItem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Store.StoreItem']", 'null': 'True', 'blank': 'True'}),
            'order_index': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pre_tax_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'sale': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Store.Sale']"}),
            'text': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '3000', 'blank': 'True'}),
            'vat_rate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Store.VatRate']"})
        },
        u'Store.storeitem': {
            'Meta': {'ordering': "['name']", 'object_name': 'StoreItem'},
            'brand': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Store.Brand']", 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Store.StoreItemCategory']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Store.StoreItemImport']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'pre_tax_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'price_policy': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Store.PricePolicy']", 'null': 'True', 'blank': 'True'}),
            'purchase_price': ('django.db.models.fields.DecimalField', [], {'default': 'None', 'null': 'True', 'max_digits': '9', 'decimal_places': '2', 'blank': 'True'}),
            'reference': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'stock_count': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'stock_threshold': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['Store.StoreItemTag']", 'symmetrical': 'False', 'blank': 'True'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Store.Unit']", 'null': 'True', 'blank': 'True'}),
            'vat_rate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Store.VatRate']"})
        },
        u'Store.storeitemcategory': {
            'Meta': {'ordering': "['order_index', 'name']", 'object_name': 'StoreItemCategory'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'icon': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'order_index': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'subcategories_set'", 'null': 'True', 'blank': 'True', 'to': u"orm['Store.StoreItemCategory']"}),
            'price_policy': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['Store.PricePolicy']", 'null': 'True', 'blank': 'True'})
        },
        u'Store.storeitemimport': {
            'Meta': {'object_name': 'StoreItemImport'},
            'category_lines_mode': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'data': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'default_brand': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'error_message': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'fields': ('django.db.models.fields.CharField', [], {'default': "'name,brand,reference,category,purchase_price,vat_rate'", 'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ignore_first_line': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'import_error': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'is_successful': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_import_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'margin_rate': ('django.db.models.fields.DecimalField', [], {'default': 'None', 'null': 'True', 'max_digits': '9', 'decimal_places': '2'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['Store.StoreItemTag']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'Store.storeitemproperty': {
            'Meta': {'object_name': 'StoreItemProperty'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_fullname': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'Store.storeitempropertyvalue': {
            'Meta': {'object_name': 'StoreItemPropertyValue'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Store.StoreItem']"}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Store.StoreItemProperty']"}),
            'value': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'})
        },
        u'Store.storeitemtag': {
            'Meta': {'ordering': "['order_index', 'name']", 'object_name': 'StoreItemTag'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'icon': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'order_index': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'show_always': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'Store.storemanagementactiontype': {
            'Meta': {'object_name': 'StoreManagementActionType'},
            'action_type': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['Crm.ActionType']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'readonly_status': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['Crm.ActionStatus']", 'symmetrical': 'False', 'blank': 'True'}),
            'show_amount_as_pre_tax': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'template_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'})
        },
        u'Store.unit': {
            'Meta': {'object_name': 'Unit'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'Store.vatrate': {
            'Meta': {'ordering': "['rate']", 'object_name': 'VatRate'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'})
        },
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
        }
    }

    complete_apps = ['Store']