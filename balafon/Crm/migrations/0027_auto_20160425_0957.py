# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0026_auto_20160422_1520'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpecialCaseCity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('oldname', models.CharField(default=b'None', max_length=100, verbose_name='old name')),
                ('possibilities', models.CharField(max_length=500, verbose_name='possibilities')),
                ('change_validated', models.CharField(default=0, max_length=3, verbose_name='change validated')),
                ('city', models.ForeignKey(to='Crm.City')),
            ],
        ),
        migrations.RemoveField(
            model_name='specialcasescities',
            name='city',
        ),
        migrations.DeleteModel(
            name='SpecialCasesCities',
        ),
    ]
