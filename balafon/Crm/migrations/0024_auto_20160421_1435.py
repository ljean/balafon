# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0023_auto_20160421_1201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='district_id',
            field=models.CharField(default=b'999', max_length=3),
        ),
    ]
