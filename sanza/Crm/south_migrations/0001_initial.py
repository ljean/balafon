# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'EntityType'
        db.create_table('Crm_entitytype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Account.Account'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('Crm', ['EntityType'])

        # Adding model 'ActivitySector'
        db.create_table('Crm_activitysector', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Account.Account'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('Crm', ['ActivitySector'])

        # Adding model 'Relationship'
        db.create_table('Crm_relationship', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Account.Account'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('Crm', ['Relationship'])

        # Adding model 'ZoneType'
        db.create_table('Crm_zonetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Account.Account'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('Crm', ['ZoneType'])

        # Adding model 'Zone'
        db.create_table('Crm_zone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Account.Account'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(default='', to=orm['Crm.Zone'], null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Crm.ZoneType'])),
            ('code', self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True)),
        ))
        db.send_create_signal('Crm', ['Zone'])

        # Adding model 'City'
        db.create_table('Crm_city', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Account.Account'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(default='', to=orm['Crm.Zone'], null=True, blank=True)),
        ))
        db.send_create_signal('Crm', ['City'])

        # Adding model 'Entity'
        db.create_table('Crm_entity', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Account.Account'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Crm.EntityType'])),
            ('activity_sector', self.gf('django.db.models.fields.related.ForeignKey')(default=u'', to=orm['Crm.ActivitySector'], null=True, blank=True)),
            ('relationship', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Crm.Relationship'])),
            ('relationship_date', self.gf('django.db.models.fields.DateField')(default='', null=True, blank=True)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(default=u'', max_length=100, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(default=u'', max_length=200, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(default=u'', max_length=200, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(default=u'', max_length=75, blank=True)),
            ('website', self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(default=u'', max_length=200, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(default=u'', max_length=10, blank=True)),
            ('cedex', self.gf('django.db.models.fields.CharField')(default=u'', max_length=200, blank=True)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(default=u'', to=orm['Crm.City'], null=True, blank=True)),
        ))
        db.send_create_signal('Crm', ['Entity'])

        # Adding model 'EntityRole'
        db.create_table('Crm_entityrole', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Account.Account'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('Crm', ['EntityRole'])

        # Adding model 'Membership'
        db.create_table('Crm_membership', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Crm.Entity'])),
            ('joining_date', self.gf('django.db.models.fields.DateField')(default=u'', null=True, blank=True)),
            ('leaving_date', self.gf('django.db.models.fields.DateField')(default=u'', null=True, blank=True)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(default='', to=orm['Crm.EntityRole'], null=True, blank=True)),
        ))
        db.send_create_signal('Crm', ['Membership'])

        # Adding model 'Contact'
        db.create_table('Crm_contact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('membership', self.gf('django.db.models.fields.related.OneToOneField')(related_name='contact', unique=True, to=orm['Crm.Membership'])),
            ('gender', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'', max_length=200, blank=True)),
            ('lastname', self.gf('django.db.models.fields.CharField')(default=u'', max_length=200, blank=True)),
            ('firstname', self.gf('django.db.models.fields.CharField')(default=u'', max_length=200, blank=True)),
            ('nickname', self.gf('django.db.models.fields.CharField')(default=u'', max_length=200, blank=True)),
            ('photo', self.gf('django.db.models.fields.files.ImageField')(default=u'', max_length=100, blank=True)),
            ('birth_date', self.gf('django.db.models.fields.DateField')(default=u'', null=True, blank=True)),
            ('job', self.gf('django.db.models.fields.CharField')(default=u'', max_length=200, blank=True)),
            ('main_contact', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('accept_newsletter', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('accept_3rdparty', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(default=u'', max_length=200, blank=True)),
            ('mobile', self.gf('django.db.models.fields.CharField')(default=u'', max_length=200, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(default=u'', max_length=75, blank=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(default='', max_length=100, db_index=True, blank=True)),
        ))
        db.send_create_signal('Crm', ['Contact'])

        # Adding model 'Group'
        db.create_table('Crm_group', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Account.Account'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True)),
        ))
        db.send_create_signal('Crm', ['Group'])

        # Adding unique constraint on 'Group', fields ['account', 'name']
        db.create_unique('Crm_group', ['account_id', 'name'])

        # Adding M2M table for field entities on 'Group'
        db.create_table('Crm_group_entities', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('group', models.ForeignKey(orm['Crm.group'], null=False)),
            ('entity', models.ForeignKey(orm['Crm.entity'], null=False))
        ))
        db.create_unique('Crm_group_entities', ['group_id', 'entity_id'])

        # Adding model 'OpportunityStatus'
        db.create_table('Crm_opportunitystatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Account.Account'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('Crm', ['OpportunityStatus'])

        # Adding model 'Opportunity'
        db.create_table('Crm_opportunity', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Crm.Entity'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Crm.OpportunityStatus'])),
            ('detail', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('probability', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('amount', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('ended', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
        ))
        db.send_create_signal('Crm', ['Opportunity'])

        # Adding model 'ActionType'
        db.create_table('Crm_actiontype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Account.Account'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('Crm', ['ActionType'])

        # Adding model 'Action'
        db.create_table('Crm_action', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Crm.Entity'])),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('planned_date', self.gf('django.db.models.fields.DateTimeField')(default='', null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['Crm.ActionType'], null=True, blank=True)),
            ('detail', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('opportunity', self.gf('django.db.models.fields.related.ForeignKey')(default='', to=orm['Crm.Opportunity'], null=True, blank=True)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(default='', to=orm['Crm.Contact'], null=True, blank=True)),
            ('done', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('done_date', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('in_charge', self.gf('django.db.models.fields.related.ForeignKey')(default='', to=orm['auth.User'], null=True, blank=True)),
            ('display_on_board', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('Crm', ['Action'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Group', fields ['account', 'name']
        db.delete_unique('Crm_group', ['account_id', 'name'])

        # Deleting model 'EntityType'
        db.delete_table('Crm_entitytype')

        # Deleting model 'ActivitySector'
        db.delete_table('Crm_activitysector')

        # Deleting model 'Relationship'
        db.delete_table('Crm_relationship')

        # Deleting model 'ZoneType'
        db.delete_table('Crm_zonetype')

        # Deleting model 'Zone'
        db.delete_table('Crm_zone')

        # Deleting model 'City'
        db.delete_table('Crm_city')

        # Deleting model 'Entity'
        db.delete_table('Crm_entity')

        # Deleting model 'EntityRole'
        db.delete_table('Crm_entityrole')

        # Deleting model 'Membership'
        db.delete_table('Crm_membership')

        # Deleting model 'Contact'
        db.delete_table('Crm_contact')

        # Deleting model 'Group'
        db.delete_table('Crm_group')

        # Removing M2M table for field entities on 'Group'
        db.delete_table('Crm_group_entities')

        # Deleting model 'OpportunityStatus'
        db.delete_table('Crm_opportunitystatus')

        # Deleting model 'Opportunity'
        db.delete_table('Crm_opportunity')

        # Deleting model 'ActionType'
        db.delete_table('Crm_actiontype')

        # Deleting model 'Action'
        db.delete_table('Crm_action')


    models = {
        'Account.account': {
            'Meta': {'object_name': 'Account'},
            'allowed': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'allowed_set'", 'default': "''", 'to': "orm['auth.User']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'default_country': ('django.db.models.fields.CharField', [], {'default': "'France'", 'max_length': '100'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nb_entities_allowed': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"})
        },
        'Crm.action': {
            'Meta': {'object_name': 'Action'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'default': "''", 'to': "orm['Crm.Contact']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'detail': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'display_on_board': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'done_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Crm.Entity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_charge': ('django.db.models.fields.related.ForeignKey', [], {'default': "''", 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'opportunity': ('django.db.models.fields.related.ForeignKey', [], {'default': "''", 'to': "orm['Crm.Opportunity']", 'null': 'True', 'blank': 'True'}),
            'planned_date': ('django.db.models.fields.DateTimeField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['Crm.ActionType']", 'null': 'True', 'blank': 'True'})
        },
        'Crm.actiontype': {
            'Meta': {'object_name': 'ActionType'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Account.Account']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'Crm.activitysector': {
            'Meta': {'object_name': 'ActivitySector'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Account.Account']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'Crm.city': {
            'Meta': {'object_name': 'City'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Account.Account']"}),
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
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Account.Account']"}),
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
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Account.Account']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'Crm.entitytype': {
            'Meta': {'object_name': 'EntityType'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Account.Account']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'Crm.group': {
            'Meta': {'unique_together': "(('account', 'name'),)", 'object_name': 'Group'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Account.Account']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'entities': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['Crm.Entity']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
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
        'Crm.opportunity': {
            'Meta': {'object_name': 'Opportunity'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'detail': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'ended': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Crm.Entity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'probability': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Crm.OpportunityStatus']"})
        },
        'Crm.opportunitystatus': {
            'Meta': {'object_name': 'OpportunityStatus'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Account.Account']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'Crm.relationship': {
            'Meta': {'object_name': 'Relationship'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Account.Account']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'Crm.zone': {
            'Meta': {'ordering': "['name']", 'object_name': 'Zone'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Account.Account']"}),
            'code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': "''", 'to': "orm['Crm.Zone']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Crm.ZoneType']"})
        },
        'Crm.zonetype': {
            'Meta': {'object_name': 'ZoneType'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Account.Account']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['Crm']
