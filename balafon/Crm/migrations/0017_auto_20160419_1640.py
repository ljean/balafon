# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0016_remove_specialcasescities_old_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='specialcasescities',
            name='city',
        ),
        migrations.DeleteModel(
            name='SpecialCasesCities',
        ),
    ]
