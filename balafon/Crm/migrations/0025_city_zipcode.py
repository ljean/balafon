# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0024_auto_20160421_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='zipcode',
            field=models.CharField(default=b'00000', max_length=20),
        ),
    ]
