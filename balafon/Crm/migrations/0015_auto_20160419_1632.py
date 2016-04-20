# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0014_auto_20160419_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specialcasescities',
            name='old_name',
            field=models.CharField(max_length=100),
        ),
    ]
