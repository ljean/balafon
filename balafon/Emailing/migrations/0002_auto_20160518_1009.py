# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Emailing', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='magiclink',
            options={'verbose_name': 'Magic link', 'verbose_name_plural': 'Magic links'},
        ),
    ]
