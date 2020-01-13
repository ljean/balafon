# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-09 13:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0024_actionstatus_next_on_send'),
        ('Store', '0014_saleitem_percentage'),
    ]

    operations = [
        migrations.AddField(
            model_name='storemanagementactiontype',
            name='default_readonly_status',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='Crm.ActionStatus', verbose_name='default readonly status'),
        ),
    ]
