# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0019_specialcasescities_oldname'),
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
