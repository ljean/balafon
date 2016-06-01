# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Crm', '0011_auto_20160520_1734'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='created_by',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='contact',
            name='created_by',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='entity',
            name='created_by',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True, verbose_name='created by'),
        ),
    ]
