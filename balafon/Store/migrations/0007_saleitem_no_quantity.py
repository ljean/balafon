# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0006_storeitem_only_for_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='saleitem',
            name='no_quantity',
            field=models.BooleanField(default=False, help_text='quantity and unit price are not shown on bill', verbose_name='no_quantity'),
        ),
    ]
