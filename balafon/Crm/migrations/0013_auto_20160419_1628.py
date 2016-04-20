# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0012_auto_20160419_1621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specialcasescities',
            name='old_name',
            field=models.CharField(default=b'null', max_length=100),
        ),
    ]
