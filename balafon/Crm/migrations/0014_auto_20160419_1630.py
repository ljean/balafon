# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0013_auto_20160419_1628'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specialcasescities',
            name='old_name',
            field=models.CharField(default=None, max_length=100),
        ),
    ]
