# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0027_auto_20160425_0957'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='specialcasecity',
            options={'ordering': ['city'], 'verbose_name': 'special case city', 'verbose_name_plural': 'special case cities'},
        ),
        migrations.AlterField(
            model_name='city',
            name='latitude',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='city',
            name='longitude',
            field=models.FloatField(default=0),
        ),
    ]
