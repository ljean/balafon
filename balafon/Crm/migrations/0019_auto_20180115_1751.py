# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0018_auto_20180104_1107'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionStatusTrack',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField()),
            ],
            options={
                'ordering': ('-datetime',),
                'verbose_name': 'Action state track',
                'verbose_name_plural': 'Action state tracks',
            },
        ),
        migrations.AddField(
            model_name='action',
            name='previous_status',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='Crm.ActionStatus', null=True),
        ),
        migrations.AddField(
            model_name='actiontype',
            name='track_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='actionstatustrack',
            name='action',
            field=models.ForeignKey(to='Crm.Action'),
        ),
        migrations.AddField(
            model_name='actionstatustrack',
            name='status',
            field=models.ForeignKey(to='Crm.ActionStatus'),
        ),
    ]
