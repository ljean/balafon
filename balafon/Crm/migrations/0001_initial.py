# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import balafon.utils
import balafon.Crm.models
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('subject', models.CharField(default=b'', max_length=200, verbose_name='subject', blank=True)),
                ('planned_date', models.DateTimeField(default=None, null=True, verbose_name='planned date', db_index=True, blank=True)),
                ('detail', models.TextField(default=b'', verbose_name='detail', blank=True)),
                ('priority', models.IntegerField(default=2, verbose_name='priority', choices=[(1, 'low priority'), (2, 'medium priority'), (3, 'high priority')])),
                ('done', models.BooleanField(default=False, db_index=True, verbose_name='done')),
                ('done_date', models.DateTimeField(default=None, null=True, verbose_name='done date', db_index=True, blank=True)),
                ('display_on_board', models.BooleanField(default=True, db_index=True, verbose_name='display on board')),
                ('archived', models.BooleanField(default=False, db_index=True, verbose_name='archived')),
                ('amount', models.DecimalField(decimal_places=2, default=None, max_digits=11, blank=True, null=True, verbose_name='amount')),
                ('number', models.IntegerField(default=0, help_text='This number is auto-generated based on action type.', verbose_name='number')),
                ('end_datetime', models.DateTimeField(default=None, null=True, verbose_name='end date', db_index=True, blank=True)),
                ('uuid', models.CharField(default=b'', max_length=100, db_index=True, blank=True)),
            ],
            options={
                'verbose_name': 'action',
                'verbose_name_plural': 'actions',
            },
        ),
        migrations.CreateModel(
            name='ActionDocument',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(default=b'', verbose_name='content', blank=True)),
                ('template', models.CharField(max_length=200, verbose_name='template')),
                ('action', models.OneToOneField(to='Crm.Action')),
            ],
        ),
        migrations.CreateModel(
            name='ActionMenu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('view_name', models.CharField(max_length=200, verbose_name='view_name')),
                ('icon', models.CharField(default=b'', max_length=30, verbose_name='icon', blank=True)),
                ('label', models.CharField(max_length=200, verbose_name='label')),
                ('a_attrs', models.CharField(default=b'', help_text='Example: class="colorbox-form" for colorbos display', max_length=50, verbose_name='Link args', blank=True)),
                ('order_index', models.IntegerField(default=0, verbose_name='order_index')),
            ],
            options={
                'ordering': ['order_index'],
                'verbose_name': 'action menu',
                'verbose_name_plural': 'action menus',
            },
        ),
        migrations.CreateModel(
            name='ActionSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('ordering', models.IntegerField(default=10, verbose_name='display ordering')),
            ],
            options={
                'ordering': ['ordering'],
                'verbose_name': 'action set',
                'verbose_name_plural': 'action sets',
            },
        ),
        migrations.CreateModel(
            name='ActionStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('ordering', models.IntegerField(default=10, verbose_name='display ordering')),
            ],
            options={
                'ordering': ['ordering'],
                'verbose_name': 'action status',
                'verbose_name_plural': 'action status',
            },
        ),
        migrations.CreateModel(
            name='ActionType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('subscribe_form', models.BooleanField(default=False, help_text='This action type will be proposed on the public subscribe form', verbose_name='Subscribe form')),
                ('last_number', models.IntegerField(default=0, verbose_name='last number')),
                ('number_auto_generated', models.BooleanField(default=False, verbose_name='generate number automatically')),
                ('default_template', models.CharField(default=b'', help_text='Action of this type will have a document with the given template', max_length=200, verbose_name='document template', blank=True)),
                ('is_editable', models.BooleanField(default=True, help_text='If default_template is set, define if the template has a editable content', verbose_name='is editable')),
                ('action_template', models.CharField(default=b'', help_text='Action of this type will be displayed using the given template', max_length=200, verbose_name='action template', blank=True)),
                ('order_index', models.IntegerField(default=10, verbose_name='Order')),
                ('is_amount_calculated', models.BooleanField(default=False, verbose_name='Is amount calculated')),
                ('not_assigned_when_cloned', models.BooleanField(default=False, verbose_name='Not assigned when cloned')),
                ('generate_uuid', models.BooleanField(default=False, verbose_name='Generate UUID for action')),
                ('allowed_status', models.ManyToManyField(default=None, help_text='Action of this type allow the given status', null=True, to='Crm.ActionStatus', blank=True)),
                ('default_status', models.ForeignKey(related_name='type_default_status_set', default=None, blank=True, to='Crm.ActionStatus', help_text='Default status for actions of this type', null=True)),
                ('next_action_types', models.ManyToManyField(to='Crm.ActionType', verbose_name='next action type', blank=True)),
                ('set', models.ForeignKey(default=None, blank=True, to='Crm.ActionSet', null=True, verbose_name='action set')),
            ],
            options={
                'ordering': ['order_index', 'name'],
                'verbose_name': 'action type',
                'verbose_name_plural': 'action types',
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'city',
                'verbose_name_plural': 'cities',
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('address', models.CharField(default='', max_length=200, verbose_name='address', blank=True)),
                ('address2', models.CharField(default='', max_length=200, verbose_name='address 2', blank=True)),
                ('address3', models.CharField(default='', max_length=200, verbose_name='address 3', blank=True)),
                ('zip_code', models.CharField(default='', max_length=20, verbose_name='zip code', blank=True)),
                ('cedex', models.CharField(default='', max_length=200, verbose_name='cedex', blank=True)),
                ('street_number', models.CharField(default=b'', max_length=20, verbose_name='street number', blank=True)),
                ('billing_address', models.CharField(default='', max_length=200, verbose_name='address', blank=True)),
                ('billing_address2', models.CharField(default='', max_length=200, verbose_name='address 2', blank=True)),
                ('billing_address3', models.CharField(default='', max_length=200, verbose_name='address 3', blank=True)),
                ('billing_zip_code', models.CharField(default='', max_length=20, verbose_name='zip code', blank=True)),
                ('billing_cedex', models.CharField(default='', max_length=200, verbose_name='cedex', blank=True)),
                ('billing_street_number', models.CharField(default=b'', max_length=20, verbose_name='street number', blank=True)),
                ('gender', models.IntegerField(default=0, blank=True, verbose_name='gender', choices=[(1, 'Mr'), (2, 'Mrs')])),
                ('title', models.CharField(default='', max_length=200, verbose_name='title', blank=True)),
                ('lastname', models.CharField(default='', max_length=200, verbose_name='last name', db_index=True, blank=True)),
                ('firstname', models.CharField(default='', max_length=200, verbose_name='first name', blank=True)),
                ('nickname', models.CharField(default='', max_length=200, verbose_name='nickname', blank=True)),
                ('photo', models.ImageField(default='', upload_to=balafon.Crm.models.get_contact_photo_dir, verbose_name='photo', blank=True)),
                ('birth_date', models.DateField(default=None, null=True, verbose_name='birth date', blank=True)),
                ('job', models.CharField(default='', max_length=200, verbose_name='job', blank=True)),
                ('main_contact', models.BooleanField(default=True, db_index=True, verbose_name='main contact')),
                ('accept_notifications', models.BooleanField(default=True, help_text='We may have to notify you some events (e.g. a new message).', verbose_name='accept notifications')),
                ('email_verified', models.BooleanField(default=False, verbose_name='email verified')),
                ('phone', models.CharField(default='', max_length=200, verbose_name='phone', blank=True)),
                ('mobile', models.CharField(default='', max_length=200, verbose_name='mobile', blank=True)),
                ('email', models.EmailField(default='', max_length=254, verbose_name='email', blank=True)),
                ('uuid', models.CharField(default=b'', max_length=100, db_index=True, blank=True)),
                ('notes', models.TextField(default=b'', verbose_name='notes', blank=True)),
                ('has_left', models.BooleanField(default=False, verbose_name='has left')),
                ('favorite_language', models.CharField(default=b'', max_length=10, verbose_name='favorite language', blank=True, choices=[(b'', 'Par d\xe9faut'), (b'fr', 'Fran\xe7ais'), (b'en', 'English')])),
                ('billing_city', models.ForeignKey(related_name='contact_billing_set', default=None, blank=True, to='Crm.City', null=True, verbose_name='city')),
            ],
            options={
                'ordering': ('lastname', 'firstname'),
                'verbose_name': 'contact',
                'verbose_name_plural': 'contacts',
            },
        ),
        migrations.CreateModel(
            name='ContactCustomFieldValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField(verbose_name='value')),
                ('contact', models.ForeignKey(to='Crm.Contact')),
            ],
            options={
                'verbose_name': 'contact custom field value',
                'verbose_name_plural': 'contact custom field values',
            },
        ),
        migrations.CreateModel(
            name='ContactsImport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('import_file', models.FileField(help_text='CSV file following the import contacts format.', upload_to=balafon.Crm.models._get_import_dir, verbose_name='import file')),
                ('name', models.CharField(default='', help_text='Optional name for searching contacts more easily. If not defined, use the name of the file.', max_length=100, verbose_name='name', blank=True)),
                ('encoding', models.CharField(default=b'utf-8', max_length=50, choices=[(b'utf-8', b'utf-8'), (b'iso-8859-15', b'iso-8859-15'), (b'cp1252', b'cp1252')])),
                ('separator', models.CharField(default=b',', max_length=5, choices=[(b',', 'Coma'), (b';', 'Semi-colon')])),
                ('entity_name_from_email', models.BooleanField(default=True, verbose_name='generate entity name from email address')),
            ],
            options={
                'verbose_name': 'contact import',
                'verbose_name_plural': 'contact imports',
            },
        ),
        migrations.CreateModel(
            name='CustomField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('label', models.CharField(default=b'', max_length=100, verbose_name='label', blank=True)),
                ('model', models.IntegerField(verbose_name='model', choices=[(1, 'Entity'), (2, 'Contact')])),
                ('widget', models.CharField(default=b'', max_length=100, verbose_name='widget', blank=True)),
                ('ordering', models.IntegerField(default=10, verbose_name='display ordering')),
                ('import_order', models.IntegerField(default=0, verbose_name='import ordering')),
                ('export_order', models.IntegerField(default=0, verbose_name='export ordering')),
                ('is_link', models.BooleanField(default=False, verbose_name='is link')),
            ],
            options={
                'ordering': ('ordering', 'import_order', 'export_order'),
                'verbose_name': 'custom field',
                'verbose_name_plural': 'custom fields',
            },
        ),
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('address', models.CharField(default='', max_length=200, verbose_name='address', blank=True)),
                ('address2', models.CharField(default='', max_length=200, verbose_name='address 2', blank=True)),
                ('address3', models.CharField(default='', max_length=200, verbose_name='address 3', blank=True)),
                ('zip_code', models.CharField(default='', max_length=20, verbose_name='zip code', blank=True)),
                ('cedex', models.CharField(default='', max_length=200, verbose_name='cedex', blank=True)),
                ('street_number', models.CharField(default=b'', max_length=20, verbose_name='street number', blank=True)),
                ('billing_address', models.CharField(default='', max_length=200, verbose_name='address', blank=True)),
                ('billing_address2', models.CharField(default='', max_length=200, verbose_name='address 2', blank=True)),
                ('billing_address3', models.CharField(default='', max_length=200, verbose_name='address 3', blank=True)),
                ('billing_zip_code', models.CharField(default='', max_length=20, verbose_name='zip code', blank=True)),
                ('billing_cedex', models.CharField(default='', max_length=200, verbose_name='cedex', blank=True)),
                ('billing_street_number', models.CharField(default=b'', max_length=20, verbose_name='street number', blank=True)),
                ('name', models.CharField(max_length=200, verbose_name='name', db_index=True)),
                ('description', models.CharField(default=b'', max_length=200, verbose_name='description', blank=True)),
                ('relationship_date', models.DateField(default=None, null=True, verbose_name='relationship date', blank=True)),
                ('logo', models.ImageField(default='', upload_to=balafon.Crm.models.get_entity_logo_dir, verbose_name='logo', blank=True)),
                ('phone', models.CharField(default='', max_length=200, verbose_name='phone', blank=True)),
                ('fax', models.CharField(default='', max_length=200, verbose_name='fax', blank=True)),
                ('email', models.EmailField(default='', max_length=254, verbose_name='email', blank=True)),
                ('website', models.CharField(default=b'', max_length=200, verbose_name='web site', blank=True)),
                ('notes', models.TextField(default=b'', verbose_name='notes', blank=True)),
                ('is_single_contact', models.BooleanField(default=False, verbose_name='is single contact')),
                ('billing_city', models.ForeignKey(related_name='entity_billing_set', default=None, blank=True, to='Crm.City', null=True, verbose_name='city')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'entity',
                'verbose_name_plural': 'entities',
            },
        ),
        migrations.CreateModel(
            name='EntityCustomFieldValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField(verbose_name='value')),
                ('custom_field', models.ForeignKey(verbose_name='custom field', to='Crm.CustomField')),
                ('entity', models.ForeignKey(to='Crm.Entity')),
            ],
            options={
                'verbose_name': 'entity custom field value',
                'verbose_name_plural': 'entity custom field values',
            },
        ),
        migrations.CreateModel(
            name='EntityRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'entity role',
                'verbose_name_plural': 'entity roles',
            },
        ),
        migrations.CreateModel(
            name='EntityType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('gender', models.IntegerField(default=1, verbose_name='gender', choices=[(1, 'Male'), (2, 'Female')])),
                ('order', models.IntegerField(default=0, verbose_name='order')),
                ('logo', models.ImageField(default='', upload_to=balafon.Crm.models._get_logo_dir, verbose_name='logo', blank=True)),
                ('subscribe_form', models.BooleanField(default=True, help_text='This type will be proposed on the public subscribe form', verbose_name='Subscribe form')),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'entity type',
                'verbose_name_plural': 'entity types',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(unique=True, max_length=200, verbose_name='name', db_index=True)),
                ('description', models.CharField(default=b'', max_length=200, verbose_name='description', blank=True)),
                ('subscribe_form', models.BooleanField(default=False, help_text='This group will be proposed on the public subscribe form', verbose_name='Subscribe form')),
                ('fore_color', models.CharField(default=b'', validators=[balafon.utils.validate_rgb], max_length=7, blank=True, help_text='Fore color. Must be a rgb code. For example: #ffffff', verbose_name='Fore color')),
                ('background_color', models.CharField(default=b'', validators=[balafon.utils.validate_rgb], max_length=7, blank=True, help_text='Background color. Must be a rgb code. For example: #000000', verbose_name='Background color')),
                ('contacts', models.ManyToManyField(to='Crm.Contact', null=True, blank=True)),
                ('entities', models.ManyToManyField(to='Crm.Entity', null=True, blank=True)),
            ],
            options={
                'verbose_name': 'group',
                'verbose_name_plural': 'groups',
            },
        ),
        migrations.CreateModel(
            name='Opportunity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('detail', models.TextField(default=b'', verbose_name='detail', blank=True)),
                ('probability', models.IntegerField(default=2, verbose_name='probability', choices=[(1, 'low'), (2, 'medium'), (3, 'high')])),
                ('amount', models.DecimalField(decimal_places=2, default=None, max_digits=11, blank=True, null=True, verbose_name='amount')),
                ('ended', models.BooleanField(default=False, db_index=True, verbose_name='closed')),
                ('start_date', models.DateField(default=None, null=True, verbose_name='starting date', blank=True)),
                ('end_date', models.DateField(default=None, null=True, verbose_name='closing date', blank=True)),
                ('display_on_board', models.BooleanField(default=True, db_index=True, verbose_name='display on board')),
                ('entity', models.ForeignKey(default=None, blank=True, to='Crm.Entity', null=True)),
            ],
            options={
                'verbose_name': 'opportunity',
                'verbose_name_plural': 'opportunities',
            },
        ),
        migrations.CreateModel(
            name='OpportunityStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('ordering', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'opportunity status',
                'verbose_name_plural': 'opportunity status',
            },
        ),
        migrations.CreateModel(
            name='OpportunityType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'opportunity type',
                'verbose_name_plural': 'opportunity types',
            },
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('contact1', models.ForeignKey(related_name='relationships1', verbose_name='contact 1', to='Crm.Contact')),
                ('contact2', models.ForeignKey(related_name='relationships2', verbose_name='contact 2', to='Crm.Contact')),
            ],
            options={
                'verbose_name': 'relationship',
                'verbose_name_plural': 'relationships',
            },
        ),
        migrations.CreateModel(
            name='RelationshipType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('reverse', models.CharField(default=b'', max_length=100, verbose_name='reverse relation', blank=True)),
            ],
            options={
                'verbose_name': 'relationship type',
                'verbose_name_plural': 'relationship types',
            },
        ),
        migrations.CreateModel(
            name='SameAs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('main_contact', models.ForeignKey(default=None, blank=True, to='Crm.Contact', null=True)),
            ],
            options={
                'verbose_name': 'same as',
                'verbose_name_plural': 'sames as',
            },
        ),
        migrations.CreateModel(
            name='StreetType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'street type',
                'verbose_name_plural': 'street types',
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accept_subscription', models.BooleanField(default=False, help_text='Keep this checked if you want to receive our newsletter.', verbose_name='accept subscription')),
                ('subscription_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('unsubscription_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('contact', models.ForeignKey(to='Crm.Contact')),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('site', models.ForeignKey(blank=True, to='sites.Site', null=True)),
            ],
            options={
                'verbose_name': 'Subscription type',
                'verbose_name_plural': 'Subscription types',
            },
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('user', models.OneToOneField(null=True, default=None, to=settings.AUTH_USER_MODEL, blank=True, verbose_name='user')),
            ],
            options={
                'verbose_name': 'team member',
                'verbose_name_plural': 'team members',
            },
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('code', models.CharField(default=b'', max_length=10, verbose_name='code', blank=True)),
                ('parent', models.ForeignKey(default=None, blank=True, to='Crm.Zone', null=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'zone',
                'verbose_name_plural': 'zones',
            },
        ),
        migrations.CreateModel(
            name='ZoneType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('type', models.CharField(max_length=200, verbose_name='type')),
            ],
            options={
                'verbose_name': 'zone type',
                'verbose_name_plural': 'zone types',
            },
        ),
        migrations.AddField(
            model_name='zone',
            name='type',
            field=models.ForeignKey(to='Crm.ZoneType'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='subscription_type',
            field=models.ForeignKey(to='Crm.SubscriptionType'),
        ),
        migrations.AddField(
            model_name='relationship',
            name='relationship_type',
            field=models.ForeignKey(verbose_name='relationship type', to='Crm.RelationshipType'),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='status',
            field=models.ForeignKey(default=None, blank=True, to='Crm.OpportunityStatus', null=True),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='type',
            field=models.ForeignKey(default=None, blank=True, to='Crm.OpportunityType', null=True),
        ),
        migrations.AddField(
            model_name='entity',
            name='billing_street_type',
            field=models.ForeignKey(related_name='entity_billing_set', default=None, blank=True, to='Crm.StreetType', null=True, verbose_name='street type'),
        ),
        migrations.AddField(
            model_name='entity',
            name='city',
            field=models.ForeignKey(default=None, blank=True, to='Crm.City', null=True, verbose_name='city'),
        ),
        migrations.AddField(
            model_name='entity',
            name='imported_by',
            field=models.ForeignKey(default=None, blank=True, to='Crm.ContactsImport', null=True),
        ),
        migrations.AddField(
            model_name='entity',
            name='last_modified_by',
            field=models.ForeignKey(default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True, verbose_name='last modified by'),
        ),
        migrations.AddField(
            model_name='entity',
            name='street_type',
            field=models.ForeignKey(default=None, blank=True, to='Crm.StreetType', null=True, verbose_name='street type'),
        ),
        migrations.AddField(
            model_name='entity',
            name='type',
            field=models.ForeignKey(default=None, blank=True, to='Crm.EntityType', null=True, verbose_name='type'),
        ),
        migrations.AddField(
            model_name='contactsimport',
            name='entity_type',
            field=models.ForeignKey(default=None, to='Crm.EntityType', blank=True, help_text='All created entities will get this type. Ignored if the entity already exist.', null=True, verbose_name='entity type'),
        ),
        migrations.AddField(
            model_name='contactsimport',
            name='groups',
            field=models.ManyToManyField(default=None, to='Crm.Group', blank=True, help_text='The created entities will be added to the selected groups.', null=True, verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='contactsimport',
            name='imported_by',
            field=models.ForeignKey(verbose_name='imported by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contactcustomfieldvalue',
            name='custom_field',
            field=models.ForeignKey(verbose_name='custom field', to='Crm.CustomField'),
        ),
        migrations.AddField(
            model_name='contact',
            name='billing_street_type',
            field=models.ForeignKey(related_name='contact_billing_set', default=None, blank=True, to='Crm.StreetType', null=True, verbose_name='street type'),
        ),
        migrations.AddField(
            model_name='contact',
            name='city',
            field=models.ForeignKey(default=None, blank=True, to='Crm.City', null=True, verbose_name='city'),
        ),
        migrations.AddField(
            model_name='contact',
            name='entity',
            field=models.ForeignKey(to='Crm.Entity'),
        ),
        migrations.AddField(
            model_name='contact',
            name='imported_by',
            field=models.ForeignKey(default=None, blank=True, to='Crm.ContactsImport', null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='last_modified_by',
            field=models.ForeignKey(default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True, verbose_name='last modified by'),
        ),
        migrations.AddField(
            model_name='contact',
            name='relationships',
            field=models.ManyToManyField(default=None, to='Crm.Contact', null=True, through='Crm.Relationship', blank=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='role',
            field=models.ManyToManyField(default=None, to='Crm.EntityRole', null=True, verbose_name='Roles', blank=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='same_as',
            field=models.ForeignKey(default=None, blank=True, to='Crm.SameAs', null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='street_type',
            field=models.ForeignKey(default=None, blank=True, to='Crm.StreetType', null=True, verbose_name='street type'),
        ),
        migrations.AddField(
            model_name='city',
            name='groups',
            field=models.ManyToManyField(related_name='city_groups_set', null=True, verbose_name='group', to='Crm.Zone', blank=True),
        ),
        migrations.AddField(
            model_name='city',
            name='parent',
            field=models.ForeignKey(default=None, blank=True, to='Crm.Zone', null=True),
        ),
        migrations.AddField(
            model_name='actionmenu',
            name='action_type',
            field=models.ForeignKey(verbose_name='Action type', to='Crm.ActionType'),
        ),
        migrations.AddField(
            model_name='actionmenu',
            name='only_for_status',
            field=models.ManyToManyField(to='Crm.ActionStatus', blank=True),
        ),
        migrations.AddField(
            model_name='action',
            name='contacts',
            field=models.ManyToManyField(default=None, to='Crm.Contact', null=True, verbose_name='contacts', blank=True),
        ),
        migrations.AddField(
            model_name='action',
            name='entities',
            field=models.ManyToManyField(default=None, to='Crm.Entity', null=True, verbose_name='entities', blank=True),
        ),
        migrations.AddField(
            model_name='action',
            name='in_charge',
            field=models.ForeignKey(default=None, blank=True, to='Crm.TeamMember', null=True, verbose_name='in charge'),
        ),
        migrations.AddField(
            model_name='action',
            name='last_modified_by',
            field=models.ForeignKey(default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True, verbose_name='last modified by'),
        ),
        migrations.AddField(
            model_name='action',
            name='opportunity',
            field=models.ForeignKey(default=None, blank=True, to='Crm.Opportunity', null=True, verbose_name='opportunity'),
        ),
        migrations.AddField(
            model_name='action',
            name='parent',
            field=models.ForeignKey(default=None, blank=True, to='Crm.Action', null=True, verbose_name='parent'),
        ),
        migrations.AddField(
            model_name='action',
            name='status',
            field=models.ForeignKey(default=None, blank=True, to='Crm.ActionStatus', null=True),
        ),
        migrations.AddField(
            model_name='action',
            name='type',
            field=models.ForeignKey(default=None, blank=True, to='Crm.ActionType', null=True),
        ),
    ]
