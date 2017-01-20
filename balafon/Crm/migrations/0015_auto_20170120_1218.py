# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0014_auto_20161108_0940'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='gender_title',
            field=models.CharField(default='', help_text='Overwrites gender if defined', max_length=50, verbose_name='gender title', blank=True),
        ),
    ]
