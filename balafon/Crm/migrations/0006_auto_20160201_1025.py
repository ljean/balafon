# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0005_auto_20160129_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='gender',
            field=models.IntegerField(default=0, blank=True, verbose_name='gender', choices=[(1, 'Mr'), (2, 'Mrs'), (3, 'Mrs and Mr')]),
        ),
    ]
