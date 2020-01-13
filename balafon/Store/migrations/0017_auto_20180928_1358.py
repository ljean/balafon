# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-28 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0016_auto_20180725_0905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='saleitem',
            name='pre_tax_price',
            field=models.DecimalField(decimal_places=4, max_digits=11, verbose_name='pre-tax price'),
        ),
        migrations.AlterField(
            model_name='storeitem',
            name='pre_tax_price',
            field=models.DecimalField(decimal_places=4, max_digits=11, verbose_name='pre-tax price'),
        ),
    ]
