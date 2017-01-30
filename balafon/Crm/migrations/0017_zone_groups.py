# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0016_auto_20170130_0955'),
    ]

    operations = [
        migrations.AddField(
            model_name='zone',
            name='groups',
            field=models.ManyToManyField(related_name='children_groups_set', verbose_name='parent groups', to='Crm.Zone', blank=True),
        ),
    ]
