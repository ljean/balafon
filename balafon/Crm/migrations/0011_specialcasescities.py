# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0010_clean_same_as'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpecialCasesCities',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('possibilities', models.CharField(max_length=500)),
                ('city', models.ForeignKey(to='Crm.City')),
            ],
        ),
    ]
