# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0011_auto_20171006_1528'),
    ]

    operations = [
        migrations.AddField(
            model_name='storeitem',
            name='description',
            field=models.TextField(default=b'', verbose_name='description', blank=True),
        ),
        migrations.AddField(
            model_name='storeitem',
            name='image',
            field=models.ImageField(default=None, upload_to=b'storeitems', null=True, verbose_name='image', blank=True),
        ),
        migrations.AddField(
            model_name='storeitemcategory',
            name='default_image',
            field=models.ImageField(default=None, upload_to=b'storeitemcats', null=True, verbose_name='image', blank=True),
        ),
    ]
