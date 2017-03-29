# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0009_storemanagementactiontype_references_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='storeitem',
            name='published',
            field=models.BooleanField(default=True, verbose_name='Published'),
        ),
    ]
