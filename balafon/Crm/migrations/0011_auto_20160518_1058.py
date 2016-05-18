# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0010_clean_same_as'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpecialCaseCity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('oldname', models.CharField(default=b'None', max_length=100, verbose_name='old name')),
                ('possibilities', models.CharField(max_length=500, verbose_name='possibilities')),
                ('change_validated', models.CharField(default=0, max_length=3, verbose_name='change validated')),
            ],
            options={
                'ordering': ['city'],
                'verbose_name': 'special case city',
                'verbose_name_plural': 'special case cities',
            },
        ),
        migrations.AddField(
            model_name='city',
            name='district_id',
            field=models.CharField(default=b'999', max_length=3),
        ),
        migrations.AddField(
            model_name='city',
            name='latitude',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='city',
            name='longitude',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='city',
            name='zip_code',
            field=models.CharField(default=b'00000', max_length=20),
        ),
        migrations.AddField(
            model_name='specialcasecity',
            name='city',
            field=models.ForeignKey(to='Crm.City'),
        ),
    ]
