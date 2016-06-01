# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0004_saleanalysiscode_action_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sale',
            options={'ordering': ['-action__created'], 'verbose_name': 'Sale', 'verbose_name_plural': 'Sales'},
        ),
        migrations.AlterModelOptions(
            name='saleanalysiscode',
            options={'ordering': ('name',), 'verbose_name': 'Analysis code', 'verbose_name_plural': 'Analysis codes'},
        ),
    ]
