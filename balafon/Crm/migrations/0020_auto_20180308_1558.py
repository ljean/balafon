# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0019_auto_20180115_1751'),
    ]

    operations = [
        migrations.AddField(
            model_name='actiontype',
            name='is_default',
            field=models.BooleanField(default=False, help_text='If checked, can be added from list. Action without types are not displayed', verbose_name='is default'),
        ),
        migrations.AlterField(
            model_name='actiontype',
            name='track_status',
            field=models.BooleanField(default=False, help_text='If checked, all status changed is stored in DB', verbose_name='Track status'),
        ),
        migrations.AlterField(
            model_name='opportunity',
            name='display_on_board',
            field=models.BooleanField(default=False, db_index=True, verbose_name='display on board'),
        ),
    ]
