# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0002_auto_20160129_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='actiontype',
            name='hide_contacts_buttons',
            field=models.BooleanField(default=False, help_text='The add and remove contact buttons will be hidden', verbose_name='hide contacts buttons'),
        ),
    ]
