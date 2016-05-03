# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0029_auto_20160502_1135'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='city',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='city',
            name='longitude',
        ),
    ]
