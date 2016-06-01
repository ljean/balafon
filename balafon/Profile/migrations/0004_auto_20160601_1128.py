# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0003_contactprofile_groups_ids'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='categorypermission',
            options={'verbose_name': 'Category permission', 'verbose_name_plural': 'Category permissions'},
        ),
        migrations.AlterModelOptions(
            name='contactprofile',
            options={'verbose_name': 'Contact profile', 'verbose_name_plural': 'Contact profiles'},
        ),
    ]
