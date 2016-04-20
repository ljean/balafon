# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0011_specialcasescities'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialcasescities',
            name='change_validated',
            field=models.CharField(default=0, max_length=3),
        ),
        migrations.AddField(
            model_name='specialcasescities',
            name='old_name',
            field=models.CharField(default=None, max_length=100),
        ),
    ]
