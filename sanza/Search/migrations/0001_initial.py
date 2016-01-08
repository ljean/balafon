# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Search',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
            ],
            options={
                'verbose_name': 'search',
                'verbose_name_plural': 'searchs',
            },
        ),
        migrations.CreateModel(
            name='SearchField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field', models.CharField(max_length=100, verbose_name='field')),
                ('value', models.CharField(max_length=200, verbose_name='value')),
                ('is_list', models.BooleanField(default=False)),
                ('count', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'search field',
                'verbose_name_plural': 'search fied',
            },
        ),
        migrations.CreateModel(
            name='SearchGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('search', models.ForeignKey(verbose_name='search', to='Search.Search')),
            ],
            options={
                'verbose_name': 'search group',
                'verbose_name_plural': 'search groups',
            },
        ),
        migrations.AddField(
            model_name='searchfield',
            name='search_group',
            field=models.ForeignKey(verbose_name='search group', to='Search.SearchGroup'),
        ),
    ]
