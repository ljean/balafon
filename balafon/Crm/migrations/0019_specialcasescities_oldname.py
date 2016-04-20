# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0018_specialcasescities'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialcasescities',
            name='oldname',
            field=models.CharField(default=b'None', max_length=100),
        ),
    ]
