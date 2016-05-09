# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0033_auto_20160503_1039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='district_id',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
