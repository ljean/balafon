# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0031_auto_20160502_1143'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='geonames_valid',
            field=models.BooleanField(default=False),
        ),
    ]
