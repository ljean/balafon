# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0015_auto_20160419_1632'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='specialcasescities',
            name='old_name',
        ),
    ]
