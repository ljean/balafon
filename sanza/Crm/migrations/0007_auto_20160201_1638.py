# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0006_auto_20160201_1025'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='same_as_priority',
            field=models.IntegerField(default=0, verbose_name='same as priority'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='same_as',
            field=models.ForeignKey(default=None, blank=True, to='Crm.SameAs', null=True, verbose_name='same as'),
        ),
    ]
