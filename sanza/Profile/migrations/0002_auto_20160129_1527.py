# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorypermission',
            name='can_edit_groups',
            field=models.ManyToManyField(default=None, related_name='can_edit_perm', to='Crm.Group', blank=True),
        ),
        migrations.AlterField(
            model_name='categorypermission',
            name='can_view_groups',
            field=models.ManyToManyField(default=None, related_name='can_view_perm', to='Crm.Group', blank=True),
        ),
    ]
