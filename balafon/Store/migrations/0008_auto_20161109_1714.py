# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0007_saleitem_no_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='saleitem',
            name='is_discount',
            field=models.BooleanField(default=False, help_text='added after total on the bill', verbose_name='is discount'),
        ),
        migrations.AlterField(
            model_name='saleitem',
            name='no_quantity',
            field=models.BooleanField(default=False, help_text='quantity and unit price are not shown on bill', verbose_name='no quantity'),
        ),
    ]
