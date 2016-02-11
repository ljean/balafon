# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('coop_cms', '0002_auto_20160108_1628'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('can_edit_groups', models.ManyToManyField(default=None, related_name='can_edit_perm', null=True, to='Crm.Group', blank=True)),
                ('can_view_groups', models.ManyToManyField(default=None, related_name='can_view_perm', null=True, to='Crm.Group', blank=True)),
                ('category', models.OneToOneField(to='coop_cms.ArticleCategory')),
            ],
        ),
        migrations.CreateModel(
            name='ContactProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entity_name', models.CharField(default=b'', max_length=200, verbose_name='Entity name', blank=True)),
                ('zip_code', models.CharField(default='', max_length=20, verbose_name='Zip code', blank=True)),
                ('gender', models.IntegerField(default=0, blank=True, verbose_name='Gender', choices=[(1, 'Mr'), (2, 'Mrs')])),
                ('lastname', models.CharField(default='', max_length=200, verbose_name='last name', blank=True)),
                ('firstname', models.CharField(default='', max_length=200, verbose_name='first name', blank=True)),
                ('birth_date', models.DateField(default=None, null=True, verbose_name='birth date', blank=True)),
                ('phone', models.CharField(default='', max_length=200, verbose_name='phone', blank=True)),
                ('mobile', models.CharField(default='', max_length=200, verbose_name='mobile', blank=True)),
                ('address', models.CharField(default='', max_length=200, verbose_name='address', blank=True)),
                ('address2', models.CharField(default='', max_length=200, verbose_name='address 2', blank=True)),
                ('address3', models.CharField(default='', max_length=200, verbose_name='address 3', blank=True)),
                ('cedex', models.CharField(default='', max_length=200, verbose_name='cedex', blank=True)),
                ('subscriptions_ids', models.CharField(default=b'', max_length=100, blank=True)),
                ('city', models.ForeignKey(default=None, blank=True, to='Crm.City', null=True, verbose_name='City')),
                ('contact', models.OneToOneField(null=True, default=None, blank=True, to='Crm.Contact')),
                ('entity_type', models.ForeignKey(default=None, blank=True, to='Crm.EntityType', null=True, verbose_name='Entity type')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
