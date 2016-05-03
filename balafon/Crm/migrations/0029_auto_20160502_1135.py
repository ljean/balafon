# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0028_auto_20160425_1006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='district_id',
            field=models.CharField(max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='latitude',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='longitude',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='zip_code',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
