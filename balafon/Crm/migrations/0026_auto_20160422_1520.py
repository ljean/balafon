# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0025_city_zipcode'),
    ]

    operations = [
        migrations.RenameField(
            model_name='city',
            old_name='zipcode',
            new_name='zip_code',
        ),
    ]
