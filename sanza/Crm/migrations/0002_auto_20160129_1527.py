# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='contacts',
            field=models.ManyToManyField(default=None, to='Crm.Contact', verbose_name='contacts', blank=True),
        ),
        migrations.AlterField(
            model_name='action',
            name='entities',
            field=models.ManyToManyField(default=None, to='Crm.Entity', verbose_name='entities', blank=True),
        ),
        migrations.AlterField(
            model_name='actiontype',
            name='allowed_status',
            field=models.ManyToManyField(default=None, help_text='Action of this type allow the given status', to='Crm.ActionStatus', blank=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='groups',
            field=models.ManyToManyField(related_name='city_groups_set', verbose_name='group', to='Crm.Zone', blank=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='relationships',
            field=models.ManyToManyField(default=None, to='Crm.Contact', through='Crm.Relationship', blank=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='role',
            field=models.ManyToManyField(default=None, to='Crm.EntityRole', verbose_name='Roles', blank=True),
        ),
        migrations.AlterField(
            model_name='contactsimport',
            name='groups',
            field=models.ManyToManyField(default=None, help_text='The created entities will be added to the selected groups.', verbose_name='groups', to='Crm.Group', blank=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='contacts',
            field=models.ManyToManyField(to='Crm.Contact', blank=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='entities',
            field=models.ManyToManyField(to='Crm.Entity', blank=True),
        ),
    ]
