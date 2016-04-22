# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0021_specialcasescities'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='district_id',
            field=models.IntegerField(default=999),
        ),
        migrations.AddField(
            model_name='city',
            name='latitude',
            field=models.FloatField(default=48.8534),
        ),
        migrations.AddField(
            model_name='city',
            name='longitude',
            field=models.FloatField(default=2.3488),
        ),
    ]
