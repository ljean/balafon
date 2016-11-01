# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0012_auto_20160601_1128'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailtoSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bcc', models.BooleanField(default=False, verbose_name='carbon copy')),
                ('subject', models.CharField(default=b'', help_text='Use action subject if empty', max_length=100, verbose_name='subject', blank=True)),
                ('body_template', models.TextField(default=b'', verbose_name='body template', blank=True)),
                ('action_type', models.OneToOneField(verbose_name='action type', to='Crm.ActionType')),
            ],
            options={
                'verbose_name': 'Mailto settings',
                'verbose_name_plural': 'Mailto settings',
            },
        ),
    ]
