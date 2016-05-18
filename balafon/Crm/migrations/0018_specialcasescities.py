# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0017_auto_20160419_1640'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpecialCasesCities',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('possibilities', models.CharField(max_length=500)),
                ('change_validated', models.CharField(default=0, max_length=3)),
                ('city', models.ForeignKey(to='Crm.City')),
            ],
        ),
    ]
