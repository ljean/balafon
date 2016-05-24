# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0010_clean_same_as'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='favorite_language',
            field=models.CharField(default=b'', max_length=10, verbose_name='favorite language', blank=True, choices=[(b'', 'Par d\xe9faut'), (b'fr', 'Fran\xe7ais')]),
        ),
    ]
