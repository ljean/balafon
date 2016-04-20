# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0020_auto_20160419_1651'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpecialCasesCities',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('oldname', models.CharField(default=b'None', max_length=100)),
                ('possibilities', models.CharField(max_length=500)),
                ('change_validated', models.CharField(default=0, max_length=3)),
                ('city', models.ForeignKey(to='Crm.City')),
            ],
        ),
    ]
