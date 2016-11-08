# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0013_mailtosettings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionmenu',
            name='only_for_status',
            field=models.ManyToManyField(to='Crm.ActionStatus', verbose_name='Only for status', blank=True),
        ),
    ]
