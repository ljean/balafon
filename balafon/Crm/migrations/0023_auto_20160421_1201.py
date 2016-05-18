# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0022_auto_20160421_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='district_id',
            field=models.CharField(default=999, max_length=3),
        ),
    ]
