# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0010_clean_same_as'),
        ('Store', '0003_auto_20160520_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='saleanalysiscode',
            name='action_type',
            field=models.ForeignKey(default=None, blank=True, to='Crm.ActionType', null=True, verbose_name='action type'),
        ),
    ]
