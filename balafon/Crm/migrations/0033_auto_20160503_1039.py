# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0032_city_geonames_valid'),
    ]

    operations = [
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
    ]
