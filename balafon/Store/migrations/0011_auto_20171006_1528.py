# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0010_storeitem_published'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='brand',
            options={'ordering': ['name'], 'verbose_name': 'Brand', 'verbose_name_plural': 'Brands'},
        ),
        migrations.AddField(
            model_name='storeitem',
            name='origin',
            field=models.CharField(default=b'', max_length=50, verbose_name='Origine', blank=True),
        ),
    ]
