# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0015_auto_20170120_1218'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscriptiontype',
            options={'ordering': ('order_index',), 'verbose_name': 'Subscription type', 'verbose_name_plural': 'Subscription types'},
        ),
        migrations.AddField(
            model_name='subscriptiontype',
            name='order_index',
            field=models.IntegerField(default=0, verbose_name='order index'),
        ),
    ]
