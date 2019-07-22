# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-24 10:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0025_actionstatus_allowed_on_frozen'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionNumberGenerator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=200, verbose_name='name')),
                ('number', models.IntegerField(default=0, help_text='This number is auto-generated.', verbose_name='number')),
            ],
            options={
                'verbose_name': 'action number generator',
                'verbose_name_plural': 'action number generators',
            },
        ),
        migrations.AlterModelOptions(
            name='actionmenu',
            options={'ordering': ['order_index'], 'verbose_name': 'action menu', 'verbose_name_plural': 'action menus'},
        ),
        migrations.AddField(
            model_name='actiontype',
            name='number_generator',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='Crm.ActionNumberGenerator', verbose_name='number generator'),
        ),
    ]