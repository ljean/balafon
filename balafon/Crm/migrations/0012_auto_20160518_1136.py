# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0011_auto_20160518_1058'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='city',
            name='geonames_valid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contact',
            name='latitude',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='longitude',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='entity',
            name='latitude',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='entity',
            name='longitude',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='district_id',
            field=models.CharField(max_length=10, null=True),
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
