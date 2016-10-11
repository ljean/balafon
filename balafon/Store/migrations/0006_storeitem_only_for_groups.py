# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0012_auto_20160601_1128'),
        ('Store', '0005_auto_20160601_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='storeitem',
            name='only_for_groups',
            field=models.ManyToManyField(help_text='If defined, only members of these groups will be able to see the item', to='Crm.Group', verbose_name='only for groups', blank=True),
        ),
    ]
