# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0008_auto_20160201_1656'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sameas',
            name='main_contact',
        ),
    ]
