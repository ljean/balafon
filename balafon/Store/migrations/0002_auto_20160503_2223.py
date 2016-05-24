# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SaleAnalysisCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Delivery point',
                'verbose_name_plural': 'Delivery points',
            },
        ),
        migrations.AlterField(
            model_name='sale',
            name='action',
            field=models.OneToOneField(to='Crm.Action', verbose_name='action'),
        ),
        migrations.AddField(
            model_name='sale',
            name='analysis_code',
            field=models.ForeignKey(default=None, blank=True, to='Store.SaleAnalysisCode', null=True, verbose_name='analysis code'),
        ),
    ]
