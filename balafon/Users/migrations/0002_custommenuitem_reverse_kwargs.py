# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='custommenuitem',
            name='reverse_kwargs',
            field=models.CharField(default=b'', help_text='kwargs to use for building the reverse. kw1:defaultval1,kw2,kw3:defaultval3 ', max_length=100, verbose_name='reverse_kwargs', blank=True),
        ),
    ]
