# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0030_auto_20160502_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='latitude',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='city',
            name='longitude',
            field=models.FloatField(null=True),
        ),
    ]
