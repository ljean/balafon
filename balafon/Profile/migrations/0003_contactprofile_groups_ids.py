# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0002_auto_20160129_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactprofile',
            name='groups_ids',
            field=models.CharField(default=b'', max_length=100, blank=True),
        ),
    ]
